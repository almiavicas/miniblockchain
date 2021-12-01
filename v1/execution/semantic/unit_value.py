from typing import Optional
from random import randint
from hashlib import sha256
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
        self._hash = self.uv_hash()


    def uv_hash(self) -> str:
        uv_unique_str = f"""
        {str(self.amount)}{self.fingerprint_hash}{str(self.timestamp)}{str(randint(0, 2 ** 128))}
        """
        return sha256(uv_unique_str.encode()).hexdigest()


    def __eq__(self, o):
        return (
            self.tx_hash == o.tx_hash and
            self.amount == o.amount and
            self.fingerprint_hash == o.fingerprint_hash and
            self.timestamp == o.timestamp and
            self.block_hash == o.block_hash
        )


    def to_dict(self):
        return {
            "hash": self._hash,
            "tx_hash": self.tx_hash,
            "amount": self.amount,
            "fingerprint_hash": self.fingerprint_hash,
            "timestamp": self.timestamp,
            "block_hash": self.block_hash,
            "spent": self.spent,
        }


    def __str__(self):
        return dumps(self.to_dict()).replace("\\", "")


def create_utxo_from_json(data: dict) -> UnitValue:
    return UnitValue(
        data["amount"],
        data["fingerprint_hash"],
        data["timestamp"],
        data.get("tx_hash", None),
        data.get("block_hash", None),
        data.get("spent", False),
    )
