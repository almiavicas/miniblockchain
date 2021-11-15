import sys
import hashlib
from time import time

class Transaction():
    def __init__(self, sender, receipt, amount):
        self.hash = hashlib.sha256()
        self.timestamp = time()
        self.sender = sender
        self.receipt = receipt
        self.amount = amount
