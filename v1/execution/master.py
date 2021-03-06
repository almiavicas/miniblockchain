from sys import getsizeof
from typing import List, Dict
from copy import deepcopy
import json
from collections import OrderedDict
from socket import socket, errno, SOCK_DGRAM, AF_INET
from argparse import ArgumentParser
from logging import getLogger, INFO, basicConfig, FileHandler, Formatter
from multiprocessing import Process, set_start_method
from hashlib import sha256
from time import sleep, time
from json import dumps
from gnupg import GPG
from semantic.mempool import Mempool
from semantic.chain import Chain
from semantic.transaction import Transaction, create_tx_from_json
from semantic.unit_value import UnitValue
from semantic.block import Block, EMPTY_BLOCK_SIZE, create_block_from_json
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
        difficulty: int = 10000,
    ):
        self.name = name
        self.mempool = Mempool()
        self.chain = Chain()
        self.neighbors = neighbors
        self.gpg = gpg
        self.port = port
        self.block_max_size = block_max_size
        self.mean_block_creation_time = mean_block_creation_time
        self.difficulty = difficulty
        set_start_method('spawn')
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
        self.log.info("Added origin block | %s", block._hash)


    def handle_message(self, message: bytes, address: tuple, sock: socket):
        decrypted_message = self.gpg.decrypt(message.decode())
        if not decrypted_message.ok:
            raise Exception("Decryption failed with status %s" % decrypted_message.status)
        decoded_message = json.loads(str(decrypted_message))
        event = decoded_message["event"]
        data = decoded_message["data"]
        if event == Event.PRESENTATION.value:
            self.log.info("%s received from %s", Event.PRESENTATION, address)
            self.event_presentation(data, sock)
        elif event == Event.PRESENTATION_ACK.value:
            self.log.info("%s received from %s", Event.PRESENTATION_ACK, address)
            self.event_presentation_ack(data)
        elif event == Event.NEW_TRANSACTION.value:
            self.log.info("%s received from %s", Event.NEW_TRANSACTION, address)
            self.event_new_transaction(data, address, sock)
        elif event == Event.TRANSACTION.value:
            self.log.info("%s received from %s", Event.TRANSACTION, address)
            self.event_transaction(data, address, sock)
        elif event == Event.TRANSACTION_ACK.value:
            self.log.info("%s received from %s", Event.TRANSACTION_ACK, address)
            self.event_transaction_ack(data)
        elif event == Event.BLOCK.value:
            self.log.info("%s received from %s", Event.BLOCK, address)
            self.event_block(data, address, sock)
        elif event == Event.BLOCK_ACK.value:
            self.log.info("%s received from %s", Event.BLOCK_ACK, address)
            self.event_block_ack(data)
        elif event == Event.BLOCK_EXPLORE.value:
            self.log.info("%s received from %s", Event.BLOCK_EXPLORE, address)
            self.event_block_explore(data, address, sock)
        elif event == Event.TRANSACTION_EXPLORE.value:
            self.log.info("%s received from %s", Event.TRANSACTION_EXPLORE, address)
            self.event_transaction_explore(data, address, sock)


    def present(self, sock: socket):
        for n in self.neighbors.values():
            self.log.info("Sending %s to %s", Event.PRESENTATION, str(n))
            data = {"name": self.name}
            n.send_message(sock, Event.PRESENTATION.value, data, self.gpg)


    def create_miner(self) -> Process:
        self.log.info("Creating new miner")
        parent_hash = self.chain.last_block()._hash
        transactions = self.pick_transactions()
        block = Block(parent_hash, transactions, len(self.chain), self.difficulty)
        miner = Miner(self.name, self.port, block, parent_hash, self.gpg)
        return Process(target=miner.start)


    def destroy_miner(self):
        if self.miner is not None and self.miner.is_alive():
            self.log.warning("Killing miner")
            self.miner.terminate()
            self.miner = None


    def pick_transactions(self) -> OrderedDict:
        """Pick transactions from mempool for a block"""
        picked_txs = OrderedDict()
        for tx in self.mempool:
            od_size = getsizeof(picked_txs)
            tx_size = getsizeof(tx)
            if EMPTY_BLOCK_SIZE + od_size + tx_size > self.block_max_size:
                break
            picked_txs[tx._hash] = tx
        self.log.info("Picked %d transactions for new miner (%d in mempool)", len(picked_txs), len(self.mempool))
        return picked_txs


    def calculate_difficulty(self, parent_block, block) -> int:
        if(abs(block.timestamp - parent_block.timestamp) < (self.mean_block_creation_time * 60) + 5):
            self.log.info("Very short block mining time - The difficulty of mining a new block will be increased | %s", block._hash)
            return self.difficulty + 1
        elif(abs(block.timestamp - parent_block.timestamp) > (self.mean_block_creation_time * 60) - 5):
            self.log.info("Very long block mining time - The difficulty of mining a new block will be decreased| %s", block._hash)
            return self.difficulty - 1

        return self.difficulty



    def event_presentation(self, data: dict, sock: socket):
        n = self.neighbors[data["name"]]
        n.is_active = True
        data = {"name": self.name}
        n.send_message(sock, Event.PRESENTATION_ACK.value, data, self.gpg)


    def event_presentation_ack(self, data: dict):
        n = self.neighbors[data["name"]]
        n.is_active = True


    def event_new_transaction(self, data: dict, address: tuple, sock: socket):
        signature = data["signature"]
        fingerprint = data["fingerprint"]
        tx = None
        try:
            tx = self.validate_transaction(signature, fingerprint)
            response_data = {
                "status": "Si",
                "transaction": tx.to_dict()
            }
        except Exception as e:
            self.log.warning("Declined transaction: %s", str(e))
            response_data = {
                "status": "No",
                "message": str(e),
            }
        finally:
            response = {
                "event": Event.NEW_TRANSACTION_ACK.value,
                "data": response_data,
            }
            sock.sendto(dumps(response).encode(), address)
        if tx is not None:
            self.mempool.add_transaction(tx)
            self.log.info("Transactions in mempool: %d | %s", len(self.mempool), tx._hash)
            propagation_data = {
                **data,
                "transaction": tx.to_dict(),
            }
            for n in self.neighbors.values():
                if n.is_active:
                    n.send_message(sock, Event.TRANSACTION.value, propagation_data, self.gpg)


    def event_transaction(self, data: dict, address: tuple, sock: socket):
        signature = data["signature"]
        fingerprint = data["fingerprint"]
        tx_json = data["transaction"]
        tx = create_tx_from_json(tx_json)
        sender_host, sender_port = address
        validated = False
        # Validation
        try:
            self.validate_transaction(signature, fingerprint)
            validated = True
            response_data = {
                "status": "Si",
            }
        except Exception as e:
            self.log.warning("Declined transaction: %s", str(e))
            response_data = {
                "status": "No",
                "message": str(e),
            }
        finally:
            sender = next(filter(lambda n: n.port == sender_port, self.neighbors.values()), None)
            if sender is not None:
                sender.send_message(sock, Event.TRANSACTION_ACK.value, response_data, self.gpg)
        # Insertion
        if validated and self.mempool.find_transaction(tx._hash) is None:
            self.mempool.add_transaction(tx)
            self.log.info("Transactions in mempool: %d | %s", len(self.mempool), tx._hash)
            # Propagation
            for n in self.neighbors.values():
                if n.is_active and n.port != sender_port:
                    n.send_message(sock, Event.TRANSACTION.value, data, self.gpg)


    def event_transaction_ack(self, data: dict):
        self.log.info("%s %s", Event.TRANSACTION_ACK, data)


    def event_block(self, data: dict, address: tuple, sock: socket):
        block_dict: dict = data["block"]
        block = create_block_from_json(block_dict)
        sender_host, sender_port = address
        validated = False
        # Validation
        try:
            self.validate_block(block)
            validated = True
            response = {
                "status": "Si",
            }
        except Exception as e:
            self.log.warning("Declined block: %s | %s", str(e), block._hash)
            response = {
                "status": "No",
                "message": str(e),
            }
        finally:
            sender = next(filter(lambda n: n.port == sender_port, self.neighbors.values()), None)
            if sender is not None:
                sender.send_message(sock, Event.BLOCK_ACK.value, response, self.gpg)
            elif not validated:
                # Enter here if the sender is the miner and the block was invalid
                self.destroy_miner()
                self.miner = self.create_miner()
                self.miner.start()
                return
        if validated and self.chain.find_block_by_hash(block._hash) is None:
            # Insertion
            self.difficulty = self.calculate_difficulty(self.chain.last_block(), block)
            self.log.info("Adding block %d | %s", block.index, block._hash)
            self.chain.insert_block(block)
            for tx in block.transactions.values():
                self.mempool.remove_transaction(tx._hash)
            self.log.info("Removed %d transactions from mempool | %s", len(block.transactions.values()), block._hash)
            self.destroy_miner()
            self.miner = self.create_miner()
            self.miner.start()
            # Propagation
            for n in self.neighbors.values():
                if n.is_active and n.port != sender_port:
                    n.send_message(sock, Event.BLOCK.value, data, self.gpg)


    def event_block_ack(self, data: dict):
        self.log.info("%s %s", Event.BLOCK_ACK, data)


    def event_block_explore(self, data: dict, address: tuple, sock: socket):
        height = data.get("height", None)
        block_hash = data.get("hash", None)
        block = None
        if isinstance(height, int):
            block = self.chain.find_block_by_height(height)
        elif isinstance(block_hash, str):
            block = self.chain.find_block_by_hash(block_hash)
        response = {
            "event": Event.BLOCK_EXPLORE_ACK.value,
            "data": {
                "block": block.to_dict() if block is not None else block,
            },
        }
        sock.sendto(dumps(response).replace("\\", "").encode(), address)


    def event_transaction_explore(self, data: dict, address: tuple, sock: socket):
        tx_hash = data.get("hash", None)
        tx = None
        if isinstance(tx_hash, str):
            tx = self.chain.find_tx_by_hash(tx_hash)
        response = {
            "event": Event.TRANSACTION_EXPLORE_ACK.value,
            "data": {
                "transaction": tx.to_dict(),
            },
        }
        sock.sendto(dumps(response).replace("\\", "").encode(), address)


    def event_log_dir(self, data: dict):
        pass


    def decrypt_transaction(self, signature: str, fingerprint: str) -> Transaction:
        verified = self.gpg.verify(signature)
        self.log.info("Message signed by fingerprint %s", verified.fingerprint)
        decrypted_message = self.gpg.decrypt(signature)
        tx_json = json.loads(str(decrypted_message))
        return create_tx_from_json(tx_json)


    def validate_block(self, block: Block):
        """Run the block validations"""
        # Validate the proof of work
        if not int(block._hash, 16) <= 2 ** (256 - block.difficulty):
            raise Exception("Proof of work was declined")
        # Validate block index
        if not block.index == len(self.chain):
            raise Exception("Block index is invalid with the current chain length")
        for tx in block.transactions.values():
            # Validate tx input utxos
            self.validate_input_utxo(tx._input)
            # Validate tx is in mempool
            if self.mempool.find_transaction(tx._hash) is None:
                raise Exception("Transaction not found in mempool")


    def validate_transaction(self, signature: str, fingerprint: str) -> Transaction:
        """
        Run the transaction validations.
        Parameters:
        -----------
        signature: str
            The transaction signed with the given fingerprint
        fingerprint : str
            The fingerprint to compare with. It will serve as the pub_key_hash
            in the p2sh script.
        """
        tx = self.decrypt_transaction(signature, fingerprint)
        # Validate tx is in mempool
        if self.mempool.find_transaction(tx._hash) is not None:
            raise Exception("Transaction hash already found in mempool")
        self.validate_input_utxo(tx._input)
        input_utxo = tx._input
        fingerprint_hash = input_utxo[0].fingerprint_hash
        # Run the p2sh script
        self.Script(
            signature,
            fingerprint,
            fingerprint_hash,
            self.gpg,
        ).execute()
        return tx


    def validate_input_utxo(self, input_utxo: List[UnitValue]):
        for utxo in input_utxo:
            utxo_tx = self.chain.find_tx_by_hash(utxo.tx_hash)
            chain_utxo = utxo_tx.find_output_utxo(utxo.fingerprint_hash)
            # Assert that the input_utxo is in the blockchain
            if not chain_utxo == utxo:
                raise Exception("Input utxo not found in chain")
            # Assert that the input_utxo is unspent
            if chain_utxo.spent:
                raise Exception("Input utxo already spent")
        # Assert that every input_utxo is from the same sender
        fingerprint_hash = input_utxo[0].fingerprint_hash
        if not all(utxo.fingerprint_hash == fingerprint_hash for utxo in input_utxo):
            raise Exception("Input utxos do not belong to the same user")


    class Script:
        "P2SH script"
        def __init__(self, sig: str, pub_key: str, pub_key_hash, gpg: GPG):
            self.script = [
                "op_checksig",
                "op_equalverify",
                pub_key_hash,
                "op_hash256",
                "op_dup",
                pub_key,
                sig,
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
            while len(self.script) > 0:
                element = self.script.pop()
                if element in commands.keys():
                    commands[element](stack)
                else:
                    stack.append(element)
            if not (len(stack) == 1 and stack[0] == True):
                raise Exception("P2SH script invalid stack status")
            return stack

        def op_dup(self, stack: List[str]):
            stack.append(stack[-1])

        def op_hash256(self, stack: List[str]):
            stack.append(sha256(stack.pop().encode()).hexdigest())

        def op_equalverify(self, stack: List[str]):
            pub_key_hash = stack.pop()
            pub_hash_a = stack.pop()
            if not pub_key_hash == pub_hash_a:
                raise Exception("op_equalverify failed")

        def op_checksig(self, stack: List[str]):
            fingerprint = stack.pop()
            signature = stack.pop()
            verified = self.gpg.verify(signature)
            stack.append(verified.fingerprint == fingerprint)


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
    if config["tamaniomaxbloque"] <= EMPTY_BLOCK_SIZE:
        raise Exception("El tamanio max del bloque es menor al tamanio del bloque vacio (%d)" % EMPTY_BLOCK_SIZE)
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
