import sys
from wallet import Wallet
from transaction import Transaction

class Identity():
    def __init__(self):
        self.name = None
        self.wallet = Wallet()
        pass

    def create_transaction(self):
        self.wallet.generate_transaction()

