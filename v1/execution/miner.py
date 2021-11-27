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
        self.block.mine(self.difficulty)
        # self.block.print_block()
        self.send_block()
        return self.block


    def send_block(self):
        # print('send block!')
        pass