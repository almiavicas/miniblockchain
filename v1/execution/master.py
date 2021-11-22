from typing import List
from logging import getLogger, INFO, basicConfig, StreamHandler, FileHandler
from threading import Thread
from gnupg import GPG
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
    def __init__(self, name: str, neighbors: List[Neighbor], log_file: str, gpg: GPG):
        self.name = name
        self.mempool = Mempool()
        self.blockchain = Chain()
        self.neighbors = neighbors
        self.gpg = gpg
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

    def event_new_transaction(signature: str, pub_key: str):
        tx = self.decrypt_transaction(signature, pub_key)
        self.validate_transaction(tx)
        pass

    def event_new_transaction_ack():
        pass

    def event_transaction(signature: str, pub_key: str, neighbor_name: str):
        pass

    def event_transaction_ack(neighbor_name: str):
        pass

    def event_block(block: Block, neighbor_name: str):
        pass

    def event_block_ack(neighbor_name: str):
        pass

    def decrypt_transaction(signature: str, pub_key: str) -> Transaction:
        pass

    def validate_transaction(tx: Transaction):
        """
        Run the P2SH algorithm to check for transaction validity.
        Parameters:
        -----------
        tx : Transaction
            The transaction with the list of input and outputs to
            validate.
        """
        pass

    class Script:
        "P2SH script"
        def __init__(self, sig: str, pub_key: str, pub_key_hash, gpg: GPG):
            self.script = [
                sig,
                pub_key,
                "op_dup",
                "op_hash256",
                pub_key_hash,
                "op_equalverify",
                "op_checksig",
            ]
            self.gpg = gpg

        def execute(self):
            stack = []
            commands = {
                "op_dup": self.op_dup,
                "op_hash256": self.op_hash256,
                "op_equalverify": self.op_equalverify,
                "op_checksig": self.op_checksig
            }
            while len(self.script > 0):
                element = self.script.pop()
                if element in commands.keys():
                    commands[element](stack)
                else:
                    stack.append(element)
            assert len(stack) == 1 and stack[0] == True
            return stack

        def op_dup(self, stack: List[str]):
            stack.append(self.stack[-1])

        def op_hash256(self, stack: List[str]):
            stack.append(sha256(stack.pop().encode("utf-8")).digest().hex())

        def op_equalverify(self, stack: List[str]):
            pub_key_hash = stack.pop()
            pub_hash_a = stack.pop()
            assert pub_key_hash == pub_hash_a

        def op_checksig(self, stack: List[str]):
            pass


def main():
    pass


if __name__ == "__main__":
    main()
