from typing import List, Optional
from hashlib import sha256
from .unit_value import UnitValue

class Transaction:


    VALID_STATUS = ("MEMPOOL", "CONFIRMED")
    def __init__(
        self,
        _input: List[UnitValue],
        output: List[UnitValue],
        timestamp: int,
        block_hash: str,
        status: Optional[str] = "MEMPOOL",
    ):
        self._input = _input
        self.output = output
        self.timestamp = timestamp
        self.block_hash = block_hash
        assert status in self.VALID_STATUS
        self.status = status


def create_tx_from_json(data: dict) -> Transaction:
    return Transaction(
        _input=list(map(lambda unit_value: UnitValue(**unit_value), data["input"])),
        output=list(map(lambda unit_value: UnitValue(**unit_value), data["output"])),
        timestamp=data["timestamp"],
        block_hash=data["block_hash"],
        status=data.get("status", None),
    )    



    
