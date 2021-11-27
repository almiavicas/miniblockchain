from typing import List, Dict
import json
from socket import socket, errno, SOCK_DGRAM, AF_INET
from argparse import ArgumentParser
from logging import getLogger, INFO, basicConfig, FileHandler, Formatter
from threading import Thread
import hashlib
from time import sleep
from json import dumps
from gnupg import GPG
from semantic.mempool import Mempool
from semantic.chain import Chain
from semantic.transaction import Transaction
from semantic.block import Block
from miner import Miner
from neighbor import Neighbor, create_neighbors
from utils import (
    create_dir,
    parse_network_file,
    get_gpg,
    get_nodes_fingerprints,
    parse_config_file,
    Event,
    LOCALHOST,
    BUFSIZE,
)

class Master:
    """
    Master class is responsible for attending requests from the external world.
    It works with an event-based execution. It listens to events and triggers
    tasks upon them.
    """
    LOG_FORMAT = "%(asctime)s | %(name)s: %(levelname)s - %(message)s"
    def __init__(
        self,
        name: str,
        neighbors: Dict[str, Neighbor],
        log_file: str,
        gpg: GPG,
        port: int,
        tamaniomaxbloque: int = 512,
        tiempopromediocreacionbloque: int = 1,
        dificultadinicial: int = 1000,
    ):
        self.name = name
        self.mempool = Mempool()
        self.chain = Chain()
        self.neighbors = neighbors
        self.gpg = gpg
        self.port = port
        self.tamaniomaxbloque = tamaniomaxbloque
        self.tiempopromediocreacionbloque = tiempopromediocreacionbloque
        self.dificultadinicial = dificultadinicial
        self.miner = None
        # The basic config goes for a default StreamHandler to the console
        basicConfig(level=INFO, format=self.LOG_FORMAT)
        self.log = getLogger(name)
        # Output logs to the log_file specified by the user
        formatter = Formatter(fmt=self.LOG_FORMAT)
        filehandler = FileHandler(log_file, mode="w")
        filehandler.setFormatter(formatter)
        self.log.addHandler(filehandler)


    def listen(self):
        self.create_origin_block()
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind((LOCALHOST, self.port))
        # sock.listen()
        self.log.info("Listening on port %d", self.port)
        self.present(sock)
        self.miner = Thread(target=self.create_miner, args=(sock,))
        self.miner.start()
        while True:
            message, addr = sock.recvfrom(BUFSIZE)
            self.handle_message(message, addr, sock)

    def create_origin_block(self):
        self.chain.insert_block(Block())

    def handle_message(self, message: bytes, address: tuple, sock: socket):
        decrypted_message = self.gpg.decrypt(message.decode())
        if not decrypted_message.ok:
            raise Exception("Decryption failed with status %s" % decrypted_message.status)
        decoded_message = json.loads(str(decrypted_message))
        event = decoded_message["event"]
        data = decoded_message["data"]
        if event == Event.PRESENTATION.value:
            self.event_presentation(data, sock)
        elif event == Event.PRESENTATION_ACK.value:
            self.event_presentation_ack(data)
        elif event == Event.BLOCK.value:
            data = json.loads(str(data))
            self.event_block(json.loads(str(data["block"])), data["name"], sock)
        elif event == Event.BLOCK_ACK.value:
            self.event_block_ack(data)


    def present(self, sock: socket):
        for n in self.neighbors.values():
            self.log.info("Sending Presentation to %s", str(n))
            data = {"name": self.name}
            n.send_message(sock, Event.PRESENTATION.value, data, self.gpg)


    def create_miner(self, sock: socket) -> Thread:
        while True:
            difficulty = 15
            last_block = self.chain.last_block()
            if last_block[0]:
                miner = Miner(self.port, Block(last_block[0], self.chain.length()), difficulty, last_block[0])
                block_mined = miner.mine()
                if miner.proof_of_work():
                    self.propagate_candidate_block(block_mined, sock)
                    self.chain.insert_block(block_mined)
            sleep(5)

    def propagate_candidate_block(self, block, sock: socket):
        for n in self.neighbors.values():
            self.log.info("Propagate candidate block to %s", str(n))
            data = dumps({
                "block": block.parser_json(),
                "name": self.name
            })
            print(data[0])
            n.send_message(sock, Event.BLOCK.value, data, self.gpg)

    def destroy_miner(self):
        pass

    def event_presentation(self, data: dict, sock: socket):
        n = self.neighbors[data["name"]]
        n.is_active = True
        self.log.info("%s received from %s", Event.PRESENTATION, str(n))
        data = {"name": self.name}
        n.send_message(sock, Event.PRESENTATION_ACK.value, data, self.gpg)

    def event_presentation_ack(self, data: dict):
        n = self.neighbors[data["name"]]
        n.is_active = True
        self.log.info("%s received from %s", Event.PRESENTATION_ACK, str(n))

    def event_new_transaction(self, signature: str, pub_key: str, sock: socket):
        tx = self.decrypt_transaction(signature, pub_key)
        self.validate_transaction(tx)
        pass

    def event_new_transaction_ack(self):
        pass

    def event_transaction(self, signature: str, pub_key: str, neighbor_name: str, sock: socket):
        pass

    def event_transaction_ack(self, neighbor_name: str):
        pass

    def event_block(self, block, neighbor_name: str, sock: socket):
        n = self.neighbors[neighbor_name]
        self.log.info("%s received from %s", Event.BLOCK, str(n))
        data = {"name": self.name}
        n.send_message(sock, Event.BLOCK_ACK.value, data, self.gpg)

    def event_block_ack(self, data: dict):
        n = self.neighbors[data["name"]]
        self.log.info("%s received from %s", Event.BLOCK_ACK, str(n))

    def decrypt_transaction(signature: str, pub_key: str) -> Transaction:
        pass

    def validate_transaction(tx: Transaction):
        """
        Run the P2SH algorithm to check for transaction validity.
        Parameters:
        -----------
        tx : Transaction
            The transaction with the list of input and outputs to
            validate.
        """
        pass

    class Script:
        "P2SH script"
        def __init__(self, sig: str, pub_key: str, pub_key_hash, gpg: GPG):
            self.script = [
                sig,
                pub_key,
                "op_dup",
                "op_hash256",
                pub_key_hash,
                "op_equalverify",
                "op_checksig",
            ]
            self.gpg = gpg

        def execute(self):
            stack = []
            commands = {
                "op_dup": self.op_dup,
                "op_hash256": self.op_hash256,
                "op_equalverify": self.op_equalverify,
                "op_checksig": self.op_checksig
            }
            while len(self.script > 0):
                element = self.script.pop()
                if element in commands.keys():
                    commands[element](stack)
                else:
                    stack.append(element)
            assert len(stack) == 1 and stack[0] == True
            return stack

        def op_dup(self, stack: List[str]):
            stack.append(self.stack[-1])

        def op_hash256(self, stack: List[str]):
            stack.append(hashlib.sha256(stack.pop().encode("utf-8")).digest().hex())

        def op_equalverify(self, stack: List[str]):
            pub_key_hash = stack.pop()
            pub_hash_a = stack.pop()
            assert pub_key_hash == pub_hash_a

        def op_checksig(self, stack: List[str]):
            pass


def main():
    parser = ArgumentParser(description="Node master process for handling events")
    parser.add_argument("name", help="Name of the node")
    parser.add_argument("logs_dir", help="Logs folder")
    parser.add_argument("network_file", help="File describing the nodes names, relations and ports")
    parser.add_argument("config_file", help="Blockchain config")
    args = parser.parse_args()
    # print(args.name, args.logs_dir, args.network_file, args.config_file)

    create_dir(args.logs_dir)
    network = parse_network_file(args.network_file)
    config = parse_config_file(args.config_file)
    # print(config)
    log_file = f"{args.logs_dir}/{args.name}.log"
    gpg: GPG = get_gpg()
    nodes_fingerprints = get_nodes_fingerprints(gpg)
    neighbors_info = network["neighbors_info"][args.name]
    neighbors = create_neighbors(network["ports_info"], neighbors_info, nodes_fingerprints)
    node_port = network["ports_info"][args.name]
    node = Master(args.name, neighbors, log_file, gpg, node_port, **config)
    node.listen()
    


if __name__ == "__main__":
    main()
