from typing import List
from .transaction import Transaction

class Mempool:

    def __init__(self):
        self.transactions: List[Transaction] = []

    def add_transaction(self, tx: Transaction):
        pass

    def get_transaction(self) -> Transaction:
        pass

    def remove_transaction(self, tx_hash):
        pass

    