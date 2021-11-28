from typing import List, Optional
from hashlib import sha256
from json import dumps
from time import time
from .unit_value import UnitValue

class Transaction:


    VALID_STATUS = ("MEMPOOL", "CONFIRMED")
    def __init__(
        self,
        _input: List[UnitValue],
        output: List[UnitValue],
        timestamp: float,
        block_hash: str,
        status: Optional[str] = "MEMPOOL",
    ):
        self._hash = sha256(bytes(int(time()))).hexdigest()
        self._input = _input
        for utxo in output:
            utxo.tx_hash = self._hash
        self.output = output
        self.timestamp = timestamp
        self.block_hash = block_hash
        self.status = status


    @property
    def status(self):
        return self._status


    @status.setter
    def status(self, value: str):
        assert value in self.VALID_STATUS
        self._status = value


    def __eq__(self, o):
        # TODO: Define what equality means between two transactions
        return True


    def __str__(self):
        return dumps({
            "inputs": dumps([str(uv) for uv in self._input]),
            "outputs": dumps([str(uv) for uv in self.output]),
            "timestamp": self.timestamp,
            "block_hash": self.block_hash,
            "status": self.status,
        }).replace("\\", "")


def create_tx_from_json(data: dict) -> Transaction:
    return Transaction(
        _input=list(map(lambda unit_value: UnitValue(**unit_value), data["input"])),
        output=list(map(lambda unit_value: UnitValue(**unit_value), data["output"])),
        timestamp=data["timestamp"],
        block_hash=data["block_hash"],
        status=data.get("status", None),
    )    



    
