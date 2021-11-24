from typing import List, Any
from socket import socket, errno, SOCK_DGRAM, AF_INET
from argparse import ArgumentParser
from logging import getLogger, INFO, basicConfig, FileHandler, Formatter
from threading import Thread
from gnupg import GPG
from semantic.mempool import Mempool
from semantic.chain import Chain
from semantic.transaction import Transaction
from semantic.block import Block
from utils import create_dir, parse_network_file, get_gpg, parse_config_file

LOCALHOST = "127.0.0.1"
BUFSIZE = 4096

class Neighbor:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.is_active = False

    def send_message(self, sock: socket, message: str, gpg: GPG):
        # The armor=False argument is to get the message as binary data. This is useful
        # when we want to decrypt the message, because gpg decrypts by default a binary-like
        # object.
        # encrypted_message = gpg.encrypt(message, self.name, armor=False)
        # We get an Encript object from this. To check if the encryption succedded, we can
        # check if the encrypted_message.ok is True.
        # if not encrypted_message.ok:
            # raise Exception("gpg could not encrypt the message `%s`" % message)
        # To get the encrypted data we need to convert the object to a string.
        # bynary_data = str(encrypted_message)
        address = (LOCALHOST, self.port)
        sock.sendto(message.encode(), address)

    def create_neighbors(ports_config: dict, neighbor_names: List[str], node: str) -> List[Any]:
        """Create the neighbors list for a given node with the specified ports config"""
        neighbor_nodes = []
        for name in neighbor_names:
            neighbor_nodes.append(Neighbor(name, ports_config[name]))
        return neighbor_nodes

    def __str__(self):
        return f"{self.name}: {self.port} ({'IN' if not self.is_active else ''}ACTIVE)"

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
        neighbors: List[Neighbor],
        log_file: str,
        gpg: GPG,
        port: int,
        tamaniomaxbloque: int = 512,
        tiempopromediocreacionbloque: int = 1,
        dificultadinicial: int = 1000,
    ):
        self.name = name
        self.mempool = Mempool()
        self.blockchain = Chain()
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
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind((LOCALHOST, self.port))
        # sock.listen()
        self.log.info("Listening on port %d", self.port)
        self.present(sock)
        while True:
            data, addr = sock.recvfrom(BUFSIZE)
            self.log.info("Received from %s a total of %d bytes: %s", addr, len(data), data.decode())

    def present(self, sock: socket):
        for n in self.neighbors:
            n.send_message(sock, "Hello world!", self.gpg)

    def create_miner(self) -> Thread:
        pass

    def destroy_miner(self):
        pass

    def event_presentation(self):
        pass

    def event_presentation_ack(self, neighbor_name: str):
        pass

    def event_new_transaction(signature: str, pub_key: str):
        tx = self.decrypt_transaction(signature, pub_key)
        self.validate_transaction(tx)
        pass

    def event_new_transaction_ack():
        pass

    def event_transaction(signature: str, pub_key: str, neighbor_name: str):
        pass

    def event_transaction_ack(neighbor_name: str):
        pass

    def event_block(block: Block, neighbor_name: str):
        pass

    def event_block_ack(neighbor_name: str):
        pass

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
            stack.append(sha256(stack.pop().encode("utf-8")).digest().hex())

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
    # print(network)
    config = parse_config_file(args.config_file)
    # print(config)
    neighbors = Neighbor.create_neighbors(network["ports_info"], network["neighbors_info"][args.name], args.name)
    log_file = f"{args.logs_dir}/{args.name}.log"
    gpg: GPG = get_gpg()
    node_port = network["ports_info"][args.name]
    node = Master(args.name, neighbors, log_file, gpg, node_port, **config)
    node.listen()
    


if __name__ == "__main__":
    main()
