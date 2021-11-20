from hashlib import sha256
from typing import Optional
from collections import OrderedDict
from datetime import datetime
from transaction import Transaction

class Block:
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
    def __init__(self,
        parent_hash: str,
        transactions: OrderedDict,
        index: int,
        difficulty: int,
        _hash: Optional[str] = None,
        nonce: Optional[int] = None,
        timestamp: Optional[datetime] = None,
        merkle_tree_root: Optional[str] = None,
    ):
        self.transactions = transactions
        self.parent_hash = parent_hash
        self.index = index
        self.difficulty = difficulty
        if _hash is None:
            self._hash = sha256(datetime.now().isoformat().encode("utf-8")).digest().hex()
        else:
            self._hash = _hash
        self.nonce = nonce
        self.timestamp = timestamp
        self.merkle_tree_root = merkle_tree_root

    def find_merkle_tree_root(self) -> str:
        """
        Build the merkle tree from transactions and return the root hash.
        """
        pass

    def mine(self):
        """
        Mine the block with the given difficulty.
        """
        pass

    def find_tx_by_hash(self, tx_hash: string) -> Transaction:
        pass

