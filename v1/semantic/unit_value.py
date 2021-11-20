from datetime import datetime
from typing import List
from hashlib import sha256

class UnitValue:
    """
    Unit values are objects that hold value for users (or addresses).
    They are used as input for Transactions and are generated as output.
    Parameters:
    -----------
    tx_hash : str
        The transaction in which the UnitValue was generated.
    block_hash : str
        The block where the tx_hash transaction is stored.
    amount : float
        The value that this unitValue has for a user.
    pub_key : str
        The public key of the owner of the UnitValue.
    timestamp : datetime.datetime
        The date when this UnitValue was generated.
    """
    def __init__(
        self,
        tx_hash: str,
        block_hash: str,
        amount: float,
        pub_key: str,
        timestamp: datetime,
    ):
        self.tx_hash = tx_hash
        self.block_hash = block_hash
        self.amount = amount
        self.pub_key_hash = sha256(pub_key.encode("utf-8")).digest().hex()
        self.timestamp = timestamp
        self.spent = False
    
    def decrypt(self, signature: str, public_key: str) -> bool:
        """
        Run the P2SH algorithm to check if the UnitValue can be spent
        with a given signature.
        Parameters:
        -----------
        signature : str
            The private key of the owner that matches the pub_key_hash.
        public_key : str
            The public key of the owner.
        """
        script = self.Script(signature, public_key, self.pub_key_hash)
        result = script.execute()


    class Script:
        def __init__(self, sig: str, pub_key: str, pub_key_hash):
            self.script = [
                sig, 
                pub_key, 
                "op_dup", 
                "op_hash256", 
                pub_key_hash, 
                "op_equalverify", 
                "op_checksig",
            ]

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
