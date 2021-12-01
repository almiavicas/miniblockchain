from sys import getsizeof
from hashlib import sha256
from typing import Optional, OrderedDict
from json import dumps
from time import time
from .transaction import Transaction, create_tx_from_json
from .merkle import MerkleTree, Node

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

    def __init__(
        self, 
        parent_hash: str,
        transactions: OrderedDict[str, Transaction],
        index: int,
        difficulty: int,
        _hash: Optional[str] = None,
        nonce: Optional[str] = None,
        timestamp: Optional[float] = time(),
        merkle_tree_root: Optional[str] = None,
    ):
        self._parent_hash = None
        self._merkle_tree_root = None
        self._nonce = None
        self._hash = _hash
        self.parent_hash = parent_hash
        self.transactions = transactions
        self.index = index
        self.difficulty = difficulty
        self.nonce = nonce
        self.timestamp = timestamp
        self.merkle_tree_root = merkle_tree_root


    @property
    def nonce(self):
        return self._nonce


    @nonce.setter
    def nonce(self, value):
        self._nonce = value
        self._hash = self.block_hash()

    
    @property
    def merkle_tree_root(self):
        return self._merkle_tree_root

    
    @merkle_tree_root.setter
    def merkle_tree_root(self, value):
        self._merkle_tree_root = value
        self._hash = self.block_hash()


    @property
    def parent_hash(self):
        return self._parent_hash
    

    @parent_hash.setter
    def parent_hash(self, value):
        self._parent_hash = value
        self._hash = self.block_hash()


    def block_hash(self) -> str:
        block_str = f"{self.merkle_tree_root}{self.parent_hash}{self.nonce}"
        return sha256(block_str.encode()).hexdigest()


    def find_merkle_tree_root(self) -> str:
        transactions = [str(tx) for tx in self.transactions.values()]
        merkle_tree = MerkleTree(transactions)
        return merkle_tree.get_root_hash()


    def find_tx_by_hash(self, tx_hash: str) -> Transaction:
        pass


    def to_dict(self):
        return {
            "index": self.index,
            "hash": self._hash,
            "timestamp": self.timestamp,
            "parent_hash": self.parent_hash,
            "nonce":self.nonce,
            "difficulty": self.difficulty,
            "transactions": [tx.to_dict() for tx in self.transactions.values()],
            "merkle_tree_root": self.merkle_tree_root,
        }


    def __str__(self):
        return dumps(self.to_dict()).replace("\\", "")


def create_block_from_json(data: dict) -> Block:
    transactions = [create_tx_from_json(tx) for tx in data["transactions"]]
    return Block(
        parent_hash=data["parent_hash"],
        transactions={tx._hash: tx for tx in transactions},
        index=data["index"],
        difficulty=data["difficulty"],
        _hash=data.get("hash", None),
        nonce=data.get("nonce", None),
        timestamp=data.get("timestamp", None),
        merkle_tree_root=data.get("merkle_tree_root", None),
    )


EMPTY_BLOCK_SIZE = getsizeof(
    Block(
        sha256().hexdigest(),
        {},
        0,
        0,
        sha256().hexdigest(),
        0,
        0.0,
        sha256().hexdigest()
    )
)

