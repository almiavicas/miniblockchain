from typing import List, Optional
from datetime import datetime
from unit_value import UnitValue

class Transaction:


    VALID_STATUS = ("MEMPOOL", "CONFIRMED")
    def __init__(
        self,
        _input: List[UnitValue],
        output: List[UnitValue],
        timestamp: datetime,
        block_hash: str,
        status: Optional[str] = "MEMPOOL",
    ):
        self._input = _input
        self.output = output
        self.timestamp = timestamp
        self.block_hash = block_hash
        assert status in self.VALID_STATUS
        self.status = status