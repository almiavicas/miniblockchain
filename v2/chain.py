import hashlib
from block import Block
from transaction import Transaction

class Chain():
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.blocks = []
        self.pool = []
        self.pending_transactions = []
        self.create_origin_block()

    def proof_of_work(self, block):
        hash = hashlib.sha256()
        hash.update(str(block).encode('utf-8'))
        return block.hash.hexdigest() == hash.hexdigest() and int(hash.hexdigest(), 16) < 2**(256-self.difficulty) and block.previous_hash == self.blocks[-1].hash
        
    def add_to_chain(self, block):
        if self.proof_of_work(block):
            self.blocks.append(block)
            
    def add_transactions_to_pool(self, transactions):
        self.pool.append(transactions)
        
    def create_origin_block(self):
        h = hashlib.sha256()
        h.update(''.encode('utf-8'))
        origin = Block("Origin", h)
        origin.mine(self.difficulty)
        self.blocks.append(origin)
        
    def mine(self):
        if len(self.pool) > 0:
            print(self.pool)
            transactions = self.pool.pop()
            block = Block(transactions, self.blocks[-1].hash)
            block.mine(self.difficulty)
            block.set_index(self.blocks[-1].index)
            self.pending_transactions = []
            self.add_to_chain(block)
            print("\n\n==================")
            print("Hash:\t\t", block.hash.hexdigest())
            print("Previous Hash:\t", block.previous_hash.hexdigest())
            print("Index:\t\t", block.index)
            print("Nonce:\t\t", block.nonce)
            print("Transactions:\t", block.transactions)
            print("Timestamp:", block.get_timestamp_formatted())
            print("\n\n==================")

    def last_block(self):
        return self.blocks[-1]

    def new_transaction(self, sender, recipient, amount):
        transaction = { 
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.pending_transactions.append(transaction)
        return transaction

    