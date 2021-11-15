import sys
from chain import Chain
from transaction import Transaction
from time import sleep

class Node():
    def __init__(self, difficulty):
        self.chain = Chain(difficulty)
        pass


chain = Chain(15)

print("Caso para las transacciones: ")
pending_transactions = []
pending_transactions.append( chain.new_transaction("Satoshi", "Mike", "5 BTC") )
pending_transactions.append( chain.new_transaction("Mike", "Satoshi", "1 BTC") )
pending_transactions.append( chain.new_transaction("Satoshi", "Hal Finney", "5 BTC") )
chain.add_transactions_to_pool(pending_transactions)
chain.mine()

pending_transactions = []
pending_transactions.append(chain.new_transaction("Mike", "Satoshi", "5 BTC"))
pending_transactions.append(chain.new_transaction("Mike", "Alice", "0.5 BTC"))
pending_transactions.append(chain.new_transaction("Mike", "Hal Finney", "5 BTC"))
pending_transactions.append(chain.new_transaction("Mike", "Alice", "5 BTC"))
chain.add_transactions_to_pool(pending_transactions)
chain.mine()

pending_transactions = []
pending_transactions.append(chain.new_transaction("Mike", "Satoshi", "5 BTC"))
pending_transactions.append(chain.new_transaction("Satoshi", "Alice", "5 BTC"))
chain.add_transactions_to_pool(pending_transactions)
chain.mine()

sleep(10)

while True: 
    ## 1. Ingresar transacción
    ## 2. Presentación
    ## 3. Propagar transacción
    ## 4. Propagar bloque candidato
    input = input()



