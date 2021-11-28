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
        timestamp: Optional[float] = time(),
        block_hash: Optional[str] = None,
        _hash: Optional[str] = sha256(str(time()).encode()).hexdigest(),
        status: Optional[str] = "MEMPOOL",
    ):
        self._input = _input
        self._hash = _hash
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


    def find_input_utxo(self, utxo_fingerprint_hash: str) -> UnitValue:
        for utxo in self._input:
            if utxo.fingerprint_hash == utxo_fingerprint_hash:
                return utxo


    def find_output_utxo(self, utxo_fingerprint_hash: str) -> UnitValue:
        for utxo in self.output:
            if utxo.fingerprint_hash == utxo_fingerprint_hash:
                return utxo


    def __eq__(self, o):
        # TODO: Define what equality means between two transactions
        return True


    def to_dict(self):
        return {
            "hash": self._hash,
            "inputs": [uv.to_dict() for uv in self._input],
            "outputs": [uv.to_dict() for uv in self.output],
            "timestamp": self.timestamp,
            "block_hash": self.block_hash,
            "status": self.status,
        }


    def __str__(self):
        return dumps(self.to_dict()).replace("\\", "")


def create_tx_from_json(data: dict) -> Transaction:
    return Transaction(
        _input=list(map(lambda unit_value: UnitValue(**unit_value), data["inputs"])),
        output=list(map(lambda unit_value: UnitValue(**unit_value), data["outputs"])),
        timestamp=data.get("timestamp", None),
        block_hash=data.get("block_hash", None),
        _hash=data.get("hash", None),
        status=data.get("status", None),
    )



    
