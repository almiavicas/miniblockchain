from sys import getsizeof
from typing import List, Dict
from copy import deepcopy
import json
from collections import OrderedDict
from socket import socket, errno, SOCK_DGRAM, AF_INET
from argparse import ArgumentParser
from logging import getLogger, INFO, basicConfig, FileHandler, Formatter
from threading import Thread
from hashlib import sha256
from time import sleep, time
from json import dumps
from gnupg import GPG
from semantic.mempool import Mempool
from semantic.chain import Chain
from semantic.transaction import Transaction, create_tx_from_json
from semantic.unit_value import UnitValue
from semantic.block import Block, EMPTY_BLOCK_SIZE
from miner import Miner
from neighbor import Neighbor, create_neighbors
from utils import (
    create_dir,
    parse_network_file,
    get_gpg,
    get_fingerprints,
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
        block_max_size: int = 512,
        mean_block_creation_time: int = 1,
        initial_difficulty: int = 1000,
    ):
        self.name = name
        self.mempool = Mempool()
        self.chain = Chain()
        self.neighbors = neighbors
        self.gpg = gpg
        self.port = port
        self.block_max_size = block_max_size
        self.mean_block_creation_time = mean_block_creation_time
        self.initial_difficulty = initial_difficulty
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
        self.log.info("Listening on port %d", self.port)
        self.present(sock)
        self.miner = self.create_miner()
        self.miner.start()
        while True:
            message, addr = sock.recvfrom(BUFSIZE)
            self.handle_message(message, addr, sock)


    def create_origin_block(self):
        nodes_fingerprints = get_fingerprints(self.gpg, prefix="nodo")
        identities_fingerprints = get_fingerprints(self.gpg, prefix="identidad")
        identities = { **nodes_fingerprints, **identities_fingerprints }
        empty_string_hash = sha256().hexdigest()
        utxos = []
        for fingerprint in identities.values():
            fingerprint_hash = sha256(fingerprint.encode()).hexdigest()
            unit_value = UnitValue(
                10000000,
                fingerprint_hash,
                0,
                empty_string_hash,
                empty_string_hash,
            )
            utxos.append(unit_value)
        transaction = Transaction([], utxos, 0, empty_string_hash, empty_string_hash)
        transactions = OrderedDict({ transaction._hash: transaction })
        block = Block("0x00", transactions, 0, 0, empty_string_hash)
        self.chain.insert_block(block)
        self.log.info("Added origin block: %s", block)


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
        elif event == Event.NEW_TRANSACTION.value:
            self.event_new_transaction(data, address, sock)
        elif event == Event.BLOCK.value:
            self.event_block(data, address, sock)
        elif event == Event.BLOCK_ACK.value:
            self.event_block_ack(data)
        elif event == Event.BLOCK_EXPLORE.value:
            self.event_block_explore(data, address, sock)
        elif event == Event.TRANSACTION_EXPLORE.value:
            self.event_transaction_explore(data, addres, sock)


    def present(self, sock: socket):
        for n in self.neighbors.values():
            self.log.info("Sending %s to %s", Event.PRESENTATION, str(n))
            data = {"name": self.name}
            n.send_message(sock, Event.PRESENTATION.value, data, self.gpg)


    def create_miner(self) -> Thread:
        difficulty = self.calculate_difficulty()
        parent_hash = self.chain.last_block()._hash
        transactions = self.pick_transactions()
        block = Block(parent_hash, transactions, len(self.chain), difficulty)
        miner = Miner(self.name, self.port, block, parent_hash, self.gpg)
        return Thread(target=miner.start)


    def destroy_miner(self):
        if self.miner.is_alive():
            self.miner._stop()
            self.miner.join()
        self.miner = None


    def pick_transactions(self) -> OrderedDict:
        """Pick transactions from mempool for a block"""
        picked_txs = {}
        for tx in self.mempool.transactions:
            od_size = getsizeof(picked_txs)
            tx_size = getsizeof(tx)
            if EMPTY_BLOCK_SIZE + od_size + tx_size > self.block_max_size:
                break
            picked_txs[tx._hash] = tx
        return picked_txs


    def calculate_difficulty(self) -> int:
        # TODO: Calculate actual difficulty based on previous blocks
        return self.initial_difficulty


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


    def event_new_transaction(self, data: dict, address: tuple, sock: socket):
        self.log.info("%s received from %s", Event.NEW_TRANSACTION, address)
        self.log.info(data)
        signature = data["signature"]
        fingerprint = data["fingerprint"]
        tx = self.decrypt_transaction(signature, fingerprint)
        self.validate_transaction(tx)
        pass


    def event_new_transaction_ack(self, data: dict):
        pass


    def event_transaction(self, data: dict, sock: socket):
        pass


    def event_transaction_ack(self, data: dict):
        pass


    def event_block(self, data: dict, address: tuple, sock: socket):
        self.log.info("%s received from %s", Event.BLOCK, address)
        pass
        block_str = data["block"]
        block_json = json.loads(block_str)
        nodes_knowing = data["propagated_nodes"]
        nodes_knowing.append(self.name)
        self.log.info("Nodes knowing: %s", nodes_knowing)
        host, sender_port = address
        propagate_data = {
            "block": block_str,
            "propagated_nodes": nodes_knowing,
        }
        for n in self.neighbors.values():
            if n.is_active and n.name not in nodes_knowing:
                n.send_message(sock, Event.BLOCK.value, propagate_data, self.gpg)
            if n.port == sender_port:
                n.is_active = True
                ack_data = {"accepted": "yes"}
                n.send_message(sock, Event.BLOCK_ACK.value, ack_data, self.gpg)


    def event_block_ack(self, data: dict):
        pass


    # def event_block(self, block, neighbor_name: str, sock: socket):
        # TODO: Validaciones del bloque (POW) antes de propagar
        # TODO: Destruir el minador si el bloque es aceptado
        # TODO: Construir el nuevo minador
        # for n in self.neighbors.values():
        #     self.log.info("Propagate candidate block to %s", str(n))
        #     data = dumps({
        #         "block": block.parser_json(),
        #         "name": self.name
        #     })
        #     print(data[0])
        #     n.send_message(sock, Event.BLOCK.value, data, self.gpg)
        # if neighbor_name:
        #     n = self.neighbors[neighbor_name]
        #     self.log.info("%s received from %s", Event.BLOCK, str(n))
        #     data = {"name": self.name}
        #     n.send_message(sock, Event.BLOCK_ACK.value, data, self.gpg)



    def event_block_explore(self, data: dict, address: tuple, sock: socket):
        self.log.info("%s received from %s", Event.BLOCK_EXPLORE, address)
        height = data.get("height", None)
        block_hash = data.get("hash", None)
        block = None
        if isinstance(height, int):
            block = self.chain.find_block_by_height(height)
        elif isinstance(block_hash, str):
            block = self.chain.find_block_by_hash(block_hash)
        response = {
            "block": block.to_dict()
        }
        self.log.info(response)
        sock.sendto(dumps(response).replace("\\", "").encode(), address)


    def event_transaction_explore(self, data: dict, addres: tuple, sock: socket):
        pass


    def event_log_dir(self, data: dict):
        pass


    def decrypt_transaction(self, signature: str, fingerprint: str) -> Transaction:
        verified = self.gpg.verify(signature)
        self.log.info("Message signed by fringerprint %s", verified.fingerprint)
        decrypted_message = self.gpg.decrypt(signature)
        self.log.info("Received %s", str(decrypted_message))
        tx_json = json.loads(str(decrypted_message))
        return create_tx_from_json(tx_json)


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
            stack.append(sha256(stack.pop().encode()).digest().hex())

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
    nodes_fingerprints = get_fingerprints(gpg, "nodo")
    neighbors_info = network["neighbors_info"][args.name]
    neighbors = create_neighbors(network["ports_info"], neighbors_info, nodes_fingerprints)
    node_port = network["ports_info"][args.name]
    node = Master(
        args.name,
        neighbors,
        log_file,
        gpg,
        node_port,
        config["tamaniomaxbloque"],
        config["tiempopromediocreacionbloque"],
        config["dificultadinicial"],
    )
    node.listen()


if __name__ == "__main__":
    main()
