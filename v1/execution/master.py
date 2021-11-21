from typing import List
from logging import getLogger, INFO, basicConfig, StreamHandler, FileHandler, Formatter
from threading import Thread
from ..semantic.mempool import Mempool
from ..semantic.chain import Chain
from ..semantic.transaction import Transaction
from ..semantic.block import Block

class Neighbor:
    def __init__(self, name, port, pub_key):
        self.name = name
        self.port = port
        self.pub_key = pub_key
        self.is_active = False

    def send_message(self, message):
        pass

class Master:
    """
    Master class is responsible for attending requests from the external world.
    It works with an event-based execution. It listens to events and triggers
    tasks upon them.
    """
    LOG_FORMAT = "%(asctime)s | %(name)s: %(levelname)s - %(message)s"
    def __init__(self, name: str, neighbors: List[Neighbor], log_file: str):
        self.name = name
        self.mempool = Mempool()
        self.blockchain = Chain()
        self.neighbors = neighbors
        self.miner = None
        # Log config
        basicConfig(level=INFO, format=self.LOG_FORMAT)
        log = getLogger(name)
        # Output logs to the log_file specified by the user
        log.addHandler(FileHandler(log_file))
        # Output logs to the default console where the script was called from
        log.addHandler(StreamHandler())


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
