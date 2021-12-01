from typing import List, Dict
from copy import deepcopy
from execution.semantic.unit_value import UnitValue
from execution.semantic.transaction import Transaction

class Wallet:

    def __init__(self, fingerprint_hash: str):
        self.fingerprint_hash = fingerprint_hash
        self.utxos: Dict[str, UnitValue] = {}
        self.txs: Dict[str, Transaction] = {}


    def add_unit_value(self, utxo: UnitValue):
        if utxo.fingerprint_hash != self.fingerprint_hash:
            raise Exception("UTXO does not belong to Wallet owner")
        self.utxos[utxo._hash] = utxo


    def find_unit_value(self, utxo_hash: str) -> UnitValue:
        return self.utxos.get(utxo_hash, None)
    
    
    def update_unit_value(self, utxo: UnitValue):
        self.add_unit_value(utxo)


    def add_transaction(self, tx: Transaction):
        for utxo in tx._input:
            self.update_unit_value(utxo)
        for utxo in tx.output:
            try:
                self.add_unit_value(utxo)
            except Exception:
                pass
        self.txs[tx._hash] = tx


    def update_transaction(self, tx: Transaction):
        self.add_transaction(tx)


    def find_tx(self, tx_hash: str) -> Transaction:
        return self.txs.get(tx_hash, None)


    def get_utxos(self) -> List[UnitValue]:
        return list(filter(lambda x: not x.spent, self.utxos.values()))


class WalletList:

    def __init__(self):
        self.wallets = {}


    def find_wallet_by_fingerprint_hash(self, fingerprint_hash: str) -> Wallet:
        return self.wallets.get(fingerprint_hash, None)


    def create_empty_wallet(self, fingerprint_hash: str):
        self.wallets[fingerprint_hash] = Wallet(fingerprint_hash)


    def add_unit_value_to_wallet(self, fingerprint_hash: str, uv: UnitValue):
        wallet = self.wallets.get(fingerprint_hash, None)
        if wallet is not None:
            wallet.add_unit_value(uv)


    def add_tx_to_wallet(self, fingerprint_hash: str, tx: Transaction):
        wallet = self.wallets.get(fingerprint_hash, None)
        if wallet is not None:
            wallet.add_transaction(tx)
