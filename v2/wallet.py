import sys
from transaction import Transaction
import hashlib

class Wallet():

    def __init__(self, pub_key):
        self.pub_key = None
        self.priv_key = None
        self.address = hashlib.sha256(pub_key)
        pass

    def generate_transaction(self):
        pass