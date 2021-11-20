from typing import List
from threading import Thread
from ..semantic.mempool import Mempool
from ..semantic.chain import Chain
from ..semantic.transaction import Transaction
from ..semantic.block import Block
from neighbor import Neighbor

class Master:
    def __init__(self, name: str, neighbors: List[Neighbor]):
        self.name = name
        self.mempool = Mempool()
        self.blockchain = Chain()
        self.neighbors = neighbors
        self.miner = None

    def listen(self, port: int):
        pass

    def present(self):
        pass

    def create_miner(self) -> Thread:
        pass

    def destroy_miner(self):
        pass

    def event_presentation(self):
        pass

    def event_presentation_ack(self, neighbor_name: str):
        pass

    def event_new_transaction(tx: Transaction):
        pass

    def event_new_transaction_ack():
        pass

    def event_transaction(tx: Transaction, neighbor_name: str):
        pass

    def event_transaction_ack(neighbor_name: str):
        pass

    def event_block(block: Block, neighbor_name: str):
        pass

    def event_block_ack(neighbor_name: str):
        pass

    def validate_transaction(tx: Transaction):
        pass
