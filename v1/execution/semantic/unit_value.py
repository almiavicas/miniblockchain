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
    fingerprint_hash : str
        The fingerprint hash of the owner of the UnitValue.
    timestamp : float
        The date when this UnitValue was generated.
    block_hash : str
        The block where the tx_hash transaction is stored.
    """
    def __init__(
        self,
        amount: float,
        fingerprint_hash: str,
        timestamp: float,
        tx_hash: Optional[str] = None,
        block_hash: Optional[str] = None,
        spent: Optional[bool] = False,
    ):
        self.tx_hash = tx_hash
        self.amount = amount
        self.fingerprint_hash = fingerprint_hash
        self.timestamp = timestamp
        self.block_hash = block_hash
        self.spent = spent


    def __eq__(self, o):
        # TODO: Define what equality means between two UnitValues
        return (
            self.tx_hash == o.tx_hash and
            self.amount == o.amount and
            self.fingerprint_hash == o.fingerprint_hash and
            self.timestamp == o.timestamp and
            self.block_hash == o.block_hash
        )


    def to_dict(self):
        return {
            "tx_hash": self.tx_hash,
            "amount": self.amount,
            "fingerprint_hash": self.fingerprint_hash,
            "timestamp": self.timestamp,
            "block_hash": self.block_hash,
            "spent": self.spent,
        }


    def __str__(self):
        return dumps(self.to_dict()).replace("\\", "")
