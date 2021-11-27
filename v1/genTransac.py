from argparse import ArgumentParser
from typing import Dict
from random import choice
from socket import socket, AF_INET, SOCK_DGRAM
from logging import getLogger, INFO, basicConfig
from json import dumps
from gnupg import GPG
from execution.utils import (
    create_dir,
    parse_config_file,
    get_fingerprints,
    get_gpg,
    Event,
    LOCALHOST
)

class TransactionGenerator:

    LOG_FORMAT = "%(asctime)s | %(name)s: %(levelname)s - %(message)s"
    def __init__(self,
        frequency: int,
        min_input: int,
        max_input: int,
        min_output: int,
        max_output: int,
        nodes_config: Dict[str, int],
        identities_fingerprints: Dict[str, str],
        gpg: GPG,
    ):
        self.frequency = frequency
        self.min_input = min_input
        self.max_input = max_input
        self.min_output = min_output
        self.max_output = max_output
        self.nodes_config = nodes_config
        self.identities_fingerprints = identities_fingerprints
        self.gpg = gpg
        basicConfig(level=INFO, format=self.LOG_FORMAT)
        self.log = getLogger("genTransac")

    def start(self):
        sender = choice(list(self.identities_fingerprints.keys()))
        self.log.info("Creating transaction from %s", sender)
        receiver_node = choice(list(self.nodes_config.keys()))
        self.log.info("Sending Transaction to node %s", receiver_node)
        sock = socket(AF_INET, SOCK_DGRAM)
        event = Event.NEW_TRANSACTION.value
        data = "hello_world!"
        fingerprint = self.identities_fingerprints[sender]
        self.log.info("Signing with fingerprint: %s", fingerprint)
        signed_data = self.gpg.sign(data, keyid=fingerprint)
        message = dumps({
            "event": event,
            "data": {
                "fingerprint": self.identities_fingerprints[sender],
                "signature": str(signed_data),
            },
        })
        encrypted_message = self.gpg.encrypt(message, receiver_node, armor=False)
        if not encrypted_message.ok:
            raise Exception("Encryption failed with status %s" % encrypted_message.status)
        sock.sendto(str(encrypted_message).encode(), (LOCALHOST, self.nodes_config[receiver_node]))


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
    ident_fingerprints = get_fingerprints(gpg, "identidad")
    generator = TransactionGenerator(
        config["frecuencia"],
        config["numentradasmin"],
        config["numentradasmax"],
        config["numsalidasmin"],
        config["numsalidasmax"],
        nodes_info,
        ident_fingerprints,
        gpg,
    )
    generator.start()

if __name__ == "__main__":
    main()