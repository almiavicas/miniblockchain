from typing import List, OrderedDict
import collections
from copy import deepcopy
from .transaction import Transaction

class Mempool:

    def __init__(self):
        self.transactions: OrderedDict[str, Transaction] = collections.OrderedDict()


    def add_transaction(self, tx: Transaction):
        self.transactions[tx._hash] = tx


    def find_transaction(self, tx_hash: str) -> Transaction:
        return deepcopy(self.transactions.get(tx_hash, None))


    def __iter__(self):
        for tx in self.transactions.values():
            yield deepcopy(tx)


    def remove_transaction(self, tx_hash):
        del self.transactions[tx_hash]


    def __len__(self):
        return len(self.transactions.values())

    