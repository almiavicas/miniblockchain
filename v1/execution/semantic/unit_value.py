from typing import Optional
from json import dumps

class UnitValue:
    """
    Unit values are objects that hold value for users (or addresses).
    They are used as input for Transactions and are generated as output.
    Parameters:
    -----------
    tx_hash : str
        The transaction in which the UnitValue was generated.
    amount : float
        The value that this unitValue has for a user.
    pub_key : str
        The public key of the owner of the UnitValue.
    timestamp : float
        The date when this UnitValue was generated.
    block_hash : str
        The block where the tx_hash transaction is stored.
    """
    def __init__(
        self,
        tx_hash: str,
        amount: float,
        pub_key_hash: str,
        timestamp: float,
        block_hash: Optional[str] = None,
    ):
        self.tx_hash = tx_hash
        self.amount = amount
        self.pub_key_hash = pub_key_hash
        self.timestamp = timestamp
        self.block_hash = block_hash
        self.spent = False


    def __eq__(self, o):
        # TODO: Define what equality means between two UnitValues
        return True


    def __str__(self):
        return dumps({
            "tx_hash": self.tx_hash,
            "amount": self.amount,
            "pub_key_hash": self.pub_key_hash,
            "timestamp": self.timestamp,
            "block_hash": self.block_hash,
        }).replace("\\", "")
