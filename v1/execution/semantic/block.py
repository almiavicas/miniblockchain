from sys import getsizeof
from hashlib import sha256
from typing import Optional
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
    def __init__(
        self, 
        parent_hash: str,
        transactions: OrderedDict,
        index: int,
        difficulty: int,
        _hash: Optional[str] = None,
        nonce: Optional[str] = None,
        timestamp: Optional[float] = None,
        merkle_tree_root: Optional[str] = None,
    ):
        self.parent_hash = parent_hash
        self.transactions = transactions
        self.index = index
        self.difficulty = difficulty
        self._hash = _hash
        self.nonce = nonce
        self.timestamp = timestamp
        self.merkle_tree_root = merkle_tree_root


    def find_merkle_tree_root(self) -> str:
        """
        Build the merkle tree from transactions and return the root hash.
        """
        pass


    def find_tx_by_hash(self, tx_hash: str) -> Transaction:
        pass


    def __str__(self):
        return dumps({
            "index": self.index,
            "hash": self._hash,
            "timestamp": self.timestamp,
            "parent_hash": self.parent_hash,
            "nonce":self.nonce,
            "difficulty": self.difficulty,
            "transactions": dumps([str(tx) for tx in self.transactions.values()]),
            "merkle_tree_root": self.merkle_tree_root,
        }).replace("\\", "")


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