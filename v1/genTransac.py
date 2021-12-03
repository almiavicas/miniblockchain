from argparse import ArgumentParser
from typing import Dict, List
from random import choice, randrange, sample, uniform
from socket import socket, AF_INET, SOCK_DGRAM
from logging import getLogger, INFO, basicConfig
from json import loads
from hashlib import sha256
from time import time, sleep
from gnupg import GPG
from execution.utils import (
    create_dir,
    parse_config_file,
    get_fingerprints,
    get_gpg,
    Event,
    BUFSIZE,
    send_message_to_node,
)
from execution.semantic.unit_value import UnitValue
from execution.semantic.block import Block
from execution.semantic.transaction import Transaction
from utils.block_explorer import explore_by_height
from utils.transaction_explorer import explore_by_hash
from utils.wallet import WalletList

class TransactionGenerator:

    LOG_FORMAT = "%(asctime)s | %(name)s: %(levelname)s - %(message)s"
    def __init__(self,
        frequency: int,
        min_input: int,
        max_input: int,
        min_output: int,
        max_output: int,
        nodes_config: Dict[str, int],
        fingerprints: Dict[str, str],
        gpg: GPG,
    ):
        self.frequency = frequency
        self.min_input = min_input
        self.max_input = max_input
        self.min_output = min_output
        self.max_output = max_output
        self.nodes_config = nodes_config
        self.fingerprints = fingerprints
        self.wallets = WalletList()
        self.next_block = 0
        self.gpg = gpg
        self.sock = sock = socket(AF_INET, SOCK_DGRAM)
        basicConfig(level=INFO, format=self.LOG_FORMAT)
        self.log = getLogger("genTransac")


    def start(self):
        self.init_wallets()
        while True:
            sender = choice(list(self.fingerprints.keys()))
            tx = self.generate_transaction(sender)
            receiver_node = choice(list(self.nodes_config.keys()))
            self.log.info("Sending transaction from %s to %s | %s", sender, receiver_node, tx.hash)
            self.send_transaction(sender, tx, receiver_node)
            response = self.sock.recv(BUFSIZE)
            response_json = loads(response.decode())
            self.log_event(response_json["event"], receiver_node, tx.hash)
            status = response_json["data"]["status"]
            self.log.info("Transaction accepted: %s | %s", status, tx.hash)
            self.log.info("Requesting latest block")
            self.request_and_update_latest_block(receiver_node)
            self.log.info("Sleeping for %d seconds", 60 // self.frequency)
            sleep(60 // self.frequency)


    def send_transaction(self, sender: str, tx: Transaction, node_name: str):
        fingerprint = self.fingerprints[sender]
        signed_tx = self.gpg.sign(str(tx), keyid=fingerprint)
        node_port = self.nodes_config[node_name]
        data = {
            "fingerprint": fingerprint,
            "signature": str(signed_tx),
        }
        event = Event.NEW_TRANSACTION.value
        send_message_to_node(data, event, node_name, node_port, self.sock, self.gpg)


    def request_block(self, block_height: int, node_name: str) -> Block:
        node_port = self.nodes_config[node_name]
        return explore_by_height(block_height, node_name, node_port, self.sock, self.gpg)


    def request_and_update_latest_block(self, node_name: str):
        block = self.request_block(self.next_block, node_name)
        if block is not None:
            self.log.info("Got block %d. Updating wallets", self.next_block)
            self.next_block += 1
            self.update_wallets(block)
        else:
            self.log.info("No new block added")


    def update_wallets(self, block: Block):
        for tx in block.transactions.values():
            sender_fingerprint_hash = tx._input[0].fingerprint_hash
            self.wallets.add_tx_to_wallet(sender_fingerprint_hash, tx)
            for fingerprint in self.fingerprints.values():
                fingerprint_hash = sha256(fingerprint.encode()).hexdigest()
                for uv in tx.output:
                    if uv.fingerprint_hash == fingerprint_hash:
                        self.wallets.add_unit_value_to_wallet(fingerprint_hash, uv)


    def log_event(self, event: int, sender: str, tx_hash: str):
        received_event = None
        if event == Event.NEW_TRANSACTION_ACK.value:
            received_event = Event.NEW_TRANSACTION_ACK
        elif event == Event.BLOCK_EXPLORE_ACK.value:
            received_event = Event.BLOCK_EXPLORE_ACK
        self.log.info("%s received from %s | %s", received_event, sender, tx_hash)


    def init_wallets(self):
        receiver_node = choice(list(self.nodes_config.keys()))
        utxos = self.load_genesis_block_outputs(receiver_node)
        self.log.info("Got %d utxos", len(utxos))
        for fingerprint in self.fingerprints.values():
            self.wallets.create_empty_wallet(sha256(fingerprint.encode()).hexdigest())
        for uv in utxos:
            wallet = self.wallets.find_wallet_by_fingerprint_hash(uv.fingerprint_hash)
            wallet.add_unit_value(uv)
        block = self.request_block(self.next_block, receiver_node)
        while block is not None:
            self.next_block += 1
            self.update_wallets(block)
            block = self.request_block(self.next_block, receiver_node)
        


    def load_genesis_block_outputs(self, receiver_node: str) -> List[UnitValue]:
        self.log.info("Asking for genesis block to %s", receiver_node)
        self.log.info(self.next_block)
        block = self.request_block(self.next_block, receiver_node)
        self.next_block += 1
        utxos = []
        for tx in block.transactions.values():
            utxos = utxos + tx.output
        return utxos


    def generate_transaction(self, sender: str) -> Transaction:
        sender_fingerprint_hash = sha256(self.fingerprints[sender].encode()).hexdigest()
        sender_wallet = self.wallets.find_wallet_by_fingerprint_hash(sender_fingerprint_hash)
        utxos = sender_wallet.get_utxos()
        input_utxo_number = randrange(min(len(utxos), self.min_input), min(len(utxos), self.max_input) + 1)
        tx_input_utxos = sample(utxos, input_utxo_number)
        tx_input_amount = sum([utxo.amount for utxo in tx_input_utxos])
        output_utxo_number = randrange(self.min_output, self.max_input + 1)
        tx_output_utxos = []
        output_utxos_candidates = list(filter(lambda receiver: receiver != sender, self.fingerprints.keys()))
        for i in range(output_utxo_number - 1):
            uv = self.generate_unit_value(output_utxos_candidates, tx_input_amount)
            tx_input_amount -= uv.amount
            tx_output_utxos.append(uv)
        uv = self.generate_unit_value(output_utxos_candidates, tx_input_amount, tx_input_amount)
        tx_output_utxos.append(uv)
        return Transaction(tx_input_utxos, tx_output_utxos)


    def generate_unit_value(
        self,
        output_candidates: List[str],
        input_amount: float,
        min_amount = 0.0
    ) -> UnitValue:
        output_utxo_owner = choice(output_candidates)
        owner_fingerprint = self.fingerprints[output_utxo_owner]
        output_utxo_amount = uniform(min_amount, input_amount)
        return UnitValue(output_utxo_amount, sha256(owner_fingerprint.encode()).hexdigest(), time())


    def get_utxos(self, fingerprint: str) -> List[UnitValue]:
        unit_values = self.wallets[sha256(fingerprint.encode()).hexdigest()]
        utxos = list(filter(lambda x: not x.spent, unit_values))
        return utxos


def main():
    parser = ArgumentParser(description="Transactions generator")
    parser.add_argument("config_file", help="Configuration for Transactions Generation")
    parser.add_argument("nodes_file", help="File describing the nodes names and ports")
    parser.add_argument("logs_dir", help="Logs folder")
    args = parser.parse_args()
    create_dir(args.logs_dir)
    config = parse_config_file(args.config_file)
    nodes_info = parse_config_file(args.nodes_file)
    gpg = get_gpg()
    nodes_fingerprints = get_fingerprints(gpg, "nodo")
    ident_fingerprints = get_fingerprints(gpg, "identidad")
    fingerprints = { **nodes_fingerprints, **ident_fingerprints }
    generator = TransactionGenerator(
        config["frecuencia"],
        config["numentradasmin"],
        config["numentradasmax"],
        config["numsalidasmin"],
        config["numsalidasmax"],
        nodes_info,
        fingerprints,
        gpg,
    )
    generator.start()

if __name__ == "__main__":
    main()
