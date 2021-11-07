from chain import Chain

chain = Chain(20)

i = 0

while(i < 5):
    data = input("Agregar algo al blockchain: ")
    chain.add_transactions_to_pool(data)
    chain.mine()
    if i % 5 == 0:
        print(chain.blocks[i])
    i += 1

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




