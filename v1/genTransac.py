from argparse import ArgumentParser
from typing import Dict, List
from random import choice, randrange, sample, uniform
from socket import socket, AF_INET, SOCK_DGRAM
from logging import getLogger, INFO, basicConfig
from json import dumps, loads
from hashlib import sha256
from time import time, sleep
from gnupg import GPG
from execution.utils import (
    create_dir,
    parse_config_file,
    get_fingerprints,
    get_gpg,
    Event,
    LOCALHOST,
    BUFSIZE,
)
from execution.semantic.unit_value import UnitValue
from execution.semantic.block import Block, create_block_from_json
from execution.semantic.transaction import Transaction

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
        self.wallets = None
        self.gpg = gpg
        self.sock = sock = socket(AF_INET, SOCK_DGRAM)
        basicConfig(level=INFO, format=self.LOG_FORMAT)
        self.log = getLogger("genTransac")


    def start(self):
        self.init_wallets()
        while True:
            sender = choice(list(self.fingerprints.keys()))
            self.log.info("Creating transaction from %s", sender)
            tx = self.generate_transaction(sender)
            receiver_node = choice(list(self.nodes_config.keys()))
            self.log.info("Sending Transaction to %s", receiver_node)
            fingerprint = self.fingerprints[sender]
            self.log.info("Signing with fingerprint: %s", fingerprint)
            signed_data = self.gpg.sign(str(tx), keyid=fingerprint)
            request_body = {
                "fingerprint": self.fingerprints[sender],
                "signature": str(signed_data),
            }
            self.send_message(request_body, Event.NEW_TRANSACTION.value, receiver_node)
            self.log.info("Sleeping for %d seconds", 60 // self.frequency)
            sleep(60 // self.frequency)


    def init_wallets(self):
        utxos = self.load_genesis_block_outputs()
        self.log.info("Got %d utxos", len(utxos))
        self.wallets = {sha256(fp.encode()).hexdigest(): [] for fp in self.fingerprints.values()}
        for uv in utxos:
            self.wallets[uv.fingerprint_hash].append(uv)


    def load_genesis_block_outputs(self) -> List[UnitValue]:
        data = {"height": 0}
        receiver_node = choice(list(self.nodes_config.keys()))
        self.log.info("Asking for genesis block to %s", receiver_node)
        self.send_message(data, Event.BLOCK_EXPLORE.value, receiver_node)
        response = self.sock.recv(BUFSIZE)
        response_json = loads(response.decode())
        block_json = response_json["block"]
        block = create_block_from_json(block_json)
        utxos = []
        for tx in block.transactions.values():
            utxos = utxos + tx.output
        return utxos


    def generate_transaction(self, sender: str) -> Transaction:
        utxos = self.get_utxos(self.fingerprints[sender])
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


    def send_message(self, data: dict, event: int, node_name: str):
        message = dumps({
            "event": event,
            "data": data,
        })
        encrypted_message = self.gpg.encrypt(message, node_name, armor=False)
        if not encrypted_message.ok:
            raise Exception("Encryption failed with status %s" % encrypted_message.status)
        self.sock.sendto(str(encrypted_message).encode(), (LOCALHOST, self.nodes_config[node_name]))




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