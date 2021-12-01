from hashlib import sha256
from random import randint
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Dict, List
from json import dumps
from gnupg import GPG
from time import time
from utils import LOCALHOST, Event
from semantic.block import Block

class Miner:
    def __init__(self, master_name: str, master_port: int, block: Block, parent_hash, gpg: GPG):
        self.master_name = master_name
        self.master_port = master_port
        self.block = block
        self.parent_hash = parent_hash
        self.gpg = gpg


    def start(self):
        self.block.merkle_tree_root = self.block.find_merkle_tree_root()
        block = self.mine()
        # After mining, set timestamp for block, txs and utxos.
        # Also set block_hash to every txs and utxos.
        mining_timestamp = time()
        block.timestamp = mining_timestamp
        for tx in block.transactions.values():
            tx.block_hash = block._hash
            tx.timestamp = mining_timestamp
            for utxo in tx.output:
                utxo.block_hash = block._hash
        data = {
            "block": block.to_dict(),
        }
        self.send_message(data)


    def mine(self) -> Block:
        block = self.block
        while int(block._hash, 16) > 2 ** (256 - block.difficulty):
            block.nonce = randint(0, 2 ** 128)
        return block


    def send_message(self, data: dict):
        message = dumps({
            "event": Event.BLOCK.value,
            "data": data,
        })
        sock = socket(AF_INET, SOCK_DGRAM)
        encrypted_message = self.gpg.encrypt(message, self.master_name, armor=False)
        if not encrypted_message.ok:
            raise Exception("Encryption failed with status %s" % encrypted_message.status)
        address = (LOCALHOST, self.master_port)
        sock.sendto(str(encrypted_message).encode(), address)
