from hashlib import sha256
from time import time
from json import dumps
from datetime import datetime
from collections import OrderedDict
from .transaction import Transaction

class Block():
    """
    Block representation.
    A block is an object containing transactions inside a blockchain. Each
    block is added to the blockchain via mining contest between nodes. The
    mining competition is based in a proof of work (PoW) competition were
    each node needs to find a solution for a math problem.
    Blocks are also used to query the blockchain for information.
    Transactions inside the blockchain are encapsulated in blocks, so if we
    need to ask some information for transactions, then we need to access
    the blocks that are added to the blockchain.
    To add a block to the blockchain, a mining process should have
    terminated and the nodes should validate that the created block
    complies with the requested difficulty for the node.
    
    Parameters:
    ----------
    parent_hash : `str`
        The hash of the previous block in the blockchain.
    transactions : `collections.OrderedDict`
        The list of transactions included in the block.
    index : `int`
        The block number. The index can be used as a unique identifier
        that also denotes the height of the block.
    difficulty : `int`
        The difficulty to mine this block.
    _hash : `Optional[str]`
        The hash to identify this hash. It is be calculated by miners. It
        should only be given when the block is being propagated from
        another node.
    nonce : `Optional[str]`
        The nonce that solves the mining contest. It should only be given
        when the block is being propagated from another node.
    timestamp : `Optional[datetime.datetime]`
        The timestamp of the mining. It should only be given when the
        block is propagated from another node.
    merkle_tree_root : `Optional[str]`
        The merkle_tree_root of the transactions tree. It should only be
        given when the block is propagated from another node.
    """
    def __init__(self, previous_hash = None, index = 0, transactions: OrderedDict = None):
        self.index = index
        self.hash = sha256()
        self.timestamp = time()
        self.previous_hash = previous_hash
        self.nonce = 0
        self.difficulty = 0
        self.transactions = transactions
        self.merkle_tree_root = None

    def set_nonce(self, nonce):
        self.nonce = nonce

    def set_hash(self, hash):
        self.hash = hash
        self.update_hash()

    def update_hash(self):
        self.hash.update(str(self).encode('utf-8'))

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

    def find_merkle_tree_root(self) -> str:
        """
        Build the merkle tree from transactions and return the root hash.
        """
        pass

    def find_tx_by_hash(self, tx_hash: str) -> Transaction:
        pass

    def print_block(self):
        print("\n\n==================")
        if(self.previous_hash):
            print("Previous Hash:\t", self.previous_hash)
        print("Hash:\t\t", self.hash.hexdigest())
        print("Index:\t\t", self.index)
        print("Nonce:\t\t", self.nonce)
        print("Transactions:\t", self.transactions)
        print("Difficulty:", self.difficulty)
        print("Timestamp:", self.get_timestamp_formatted())
        print("\n\n==================")

    def set_index(self, previous_index):
        self.index = previous_index + 1

    def get_timestamp_formatted(self):
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
    def parser_json(self):
        return dumps({
            "index": self.index,
            "hash": self.hash.hexdigest(),
            "timestamp": self.get_timestamp_formatted(),
            "previous_hash": self.previous_hash,
            "nonce":self.nonce,
            "difficulty": self.difficulty,
            "transactions": 'self.transactions',
            "merkle_tree_roo": self.merkle_tree_root,
        })

    def __str__(self):
        return "{}{}{}".format(self.previous_hash if self.previous_hash else self.previous_hash, self.transactions, self.nonce)
