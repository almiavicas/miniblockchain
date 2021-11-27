import hashlib
import random
from semantic.block import Block

class Miner:
    def __init__(self, master_port: int, block: Block, difficulty: int,  parent_hash = None):
        self.master_port = master_port
        self.block = block
        self.difficulty = difficulty
        self.parent_hash = parent_hash

    def proof_of_work(self):
        hash = hashlib.sha256()
        hash.update(str(self.block).encode('utf-8'))
        return self.block.hash.hexdigest() == hash.hexdigest() and int(hash.hexdigest(), 16) < 2**(256-self.difficulty) and self.block.previous_hash == (self.parent_hash if self.parent_hash else None)

    def mine(self):
        self._mine()
        self.block.print_block()
        self.send_block()
        return self.block

    def _mine(self):
        self.block.set_difficulty(self.difficulty)
        self.block.hash.update(str(self.block).encode('utf-8'))
        while int(self.block.hash.hexdigest(), 16) > 2**(256-self.difficulty):
            self.block.set_nonce(random.randint(0, 10000000))
            self.block.set_hash(hashlib.sha256())


    def send_block(self):
        if self.proof_of_work():
            print('send block!')
        pass