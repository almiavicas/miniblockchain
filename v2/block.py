import hashlib
from time import time
from datetime import datetime
import random
from transaction import Transaction

class Block():
    def __init__(self, transactions, previous_hash):
        self.index = 0
        self.hash = hashlib.sha256()
        self.previous_hash = previous_hash
        self.nonce = 0
        self.timestamp = time()
        self.transactions = transactions
        
    def mine(self, difficulty):
        self.hash.update(str(self).encode('utf-8'))
        while int(self.hash.hexdigest(), 16) > 2**(256-difficulty):
            self.nonce += 1
            self.nonce = random.randint(0, 1000000)
            self.hash = hashlib.sha256()
            self.hash.update(str(self).encode('utf-8'))

    def set_index(self, previous_index):
        self.index = previous_index + 1

    def get_timestamp_formatted(self):
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
    def __str__(self):
        return "{}{}{}".format(self.previous_hash.hexdigest(), self.transactions, self.nonce)
