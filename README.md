# miniblockchain
This repository is part of a project for the course CI4852: Tópicos Especiales en Computación (Tecnologías Blockchain).

The objective is to develop a P2P application that simulates the behavior of a simplified Blockchain network. This prototype will use block and transaction definitions like the ones used by the Bitcoin network.

# Version 1
The version 1 of the miniblockchain is under the v1 folder. In order to use some scripts, you need to create a virtual environment ant install the `requirements.txt` dependencies via pip.

For working with this version, run `cd v1` before runnning any other command listed below.

## Identities generation
```bash
./genIdenti -i 10 -n 4
```
- The `-i` flag sets the total number of identities that will be generated.
- The `-n` flag specifies a number of identitites to assign to nodes. Keep in mind that using more nodes than the specified in here will cause errors when encrypting for those extra nodes.

## Nodes generation
We added some example configuration to generate nodes. To use these example files, you can run the following command
```bash
./nodo -n nodo1 -d logs/ -f example_network.txt -c example_config.txt
```
To run every node in the example config files, run the following instead
```bash
./nodo -n nodo1 -d logs/ -f example_network.txt -c example_config.txt && \
./nodo -n nodo2 -d logs/ -f example_network.txt -c example_config.txt && \
./nodo -n nodo3 -d logs/ -f example_network.txt -c example_config.txt && \
./nodo -n nodo4 -d logs/ -f example_network.txt -c example_config.txt
```

## Transactions generator
We have a transactions generator that you can use and configure to send dummy transactions to the network in a specified frequency. Use the following command to start the transactions generator:
```bash
./genTransac -f genTransac.config.txt -n genTransac.nodo.txt -d logs/
```

## Block explorer
The block explorer allows you to retrieve blocks information by requesting a specific height or specific block hash.

To use the block explorer run the following:
```bash
./exploradorBloque <node> <port> [-a <height>] [-h <hash>]
```
- The `node` parameter specifies the node identity which will receive the request. It should 
- The `port` specifies the node port.
