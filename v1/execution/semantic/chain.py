import hashlib
from .block import Block
from .transaction import Transaction
from collections import OrderedDict
class Chain():
    def __init__(self):
        self.blockchain = OrderedDict()

    def find_block_by_height(self, height: int) -> Block:
        pass

    def find_tx_by_hash(self, tx_hash: str) -> Transaction:
        pass

    def validate_block(self, block: Block) -> bool:
        pass

    def insert_block(self, block: Block):
        self.blockchain[block.hash.hexdigest()] = block

    def last_block(self):
        els = list(self.blockchain.items())
        return els[-1] if els else None

    def length(self):
        return len(list(self.blockchain.items()))