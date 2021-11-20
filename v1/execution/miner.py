from ..semantic.block import Block

class Miner:
    def __init__(self, master_port: int, block: Block):
        self.master_port = master_port
        self.block = block

    def mine(self):
        pass

    def send_block(block: Block):
        pass