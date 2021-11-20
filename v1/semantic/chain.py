from collections import OrderedDict
from block import Block
from transaction import Transaction

class Chain:
    def __init__(self):
        self.blockchain = OrderedDict()

    def find_block_by_height(height: int) -> Block:
        pass

    def find_tx_by_hash(tx_hash: string) -> Transaction:
        pass

    def validate_block(block: Block) -> bool:
        pass

    def insert_block(block: Block):
        pass