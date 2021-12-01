import hashlib
from .block import Block
from .transaction import Transaction
from collections import OrderedDict
from copy import deepcopy


class Chain():
    def __init__(self):
        self.blockchain = OrderedDict()

    def find_block_by_height(self, height: int) -> Block:
        if len(self) < height + 1:
            return None
        block = list(self.blockchain.values())[height]
        return deepcopy(block)

    def find_block_by_hash(self, _hash: str) -> Block:
        return deepcopy(self.blockchain.get(_hash, None))

    def find_tx_by_hash(self, tx_hash: str) -> Transaction:
        for block in self.blockchain.values():
            if tx_hash in block.transactions.keys():
                return deepcopy(block.transactions[tx_hash])

    def insert_block(self, block: Block):
        for tx in block.transactions.values():
            tx.status = "CONFIRMED"
            new_tx_input = []
            for utxo in tx._input:
                utxo_tx = self.find_tx_by_hash(utxo.tx_hash)
                chain_utxo = utxo_tx.find_output_utxo(utxo.fingerprint_hash)
                chain_utxo.spent = True
                new_tx_input.append(chain_utxo)
            tx._input = new_tx_input
        self.blockchain[block._hash] = block
                

    def last_block(self) -> Block:
        blocks = list(self.blockchain.values())
        return deepcopy(blocks[-1])

    def __len__(self):
        return len(list(self.blockchain.items()))