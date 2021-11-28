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

    def insert_block(self, block: Block):
        self.blockchain[block._hash] = block
        for tx in block.transactions.values():
            tx.status = "CONFIRMED"

    def last_block(self) -> Block:
        blocks = list(self.blockchain.values())
        return blocks[-1]

    def __len__(self):
        return len(list(self.blockchain.items()))