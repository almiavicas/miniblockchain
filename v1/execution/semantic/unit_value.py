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
    timestamp : int
        The date when this UnitValue was generated.
    """
    def __init__(
        self,
        tx_hash: str,
        block_hash: str,
        amount: float,
        pub_key_hash: str,
        timestamp: int,
    ):
        self.tx_hash = tx_hash
        self.block_hash = block_hash
        self.amount = amount
        self.pub_key_hash = pub_key_hash
        self.timestamp = timestamp
        self.spent = False
