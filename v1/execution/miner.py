from hashlib import sha256
from random import randint
from socket import socket
from typing import Dict, List
from json import dumps
from gnupg import GPG
from utils import LOCALHOST
from semantic.block import Block

class Miner:
    def __init__(self, master_port: int, block: Block, difficulty: int,  parent_hash = None):
        self.master_port = master_port
        self.block = block
        self.difficulty = difficulty
        self.parent_hash = parent_hash

    def proof_of_work(self):
        hash = sha256()
        hash.update(str(self.block).encode('utf-8'))
        return self.block.hash.hexdigest() == hash.hexdigest() and int(hash.hexdigest(), 16) < 2**(256-self.difficulty) and self.block.previous_hash == (self.parent_hash if self.parent_hash else None)

    def mine(self):
        self._mine()
        self.block.print_block()
        return self.block

    def _mine(self):
        self.block.set_difficulty(self.difficulty)
        self.block.hash.update(str(self.block).encode('utf-8'))
        while int(self.block.hash.hexdigest(), 16) > 2**(256-self.difficulty):
            self.block.set_nonce(randint(0, 10000000))
            self.block.set_hash(sha256())

    def send_message(self, sock: socket, event: int, data: str, gpg: GPG):
        message = dumps({
            "event": event,
            "data": data,
        })
        encrypted_message = gpg.encrypt(message, self.name, armor=False)
        if not encrypted_message.ok:
            raise Exception("Encryption failed with status %s" % encrypted_message.status)
        address = (LOCALHOST, self.port)
        sock.sendto(str(encrypted_message).encode(), address)