from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_DGRAM
from json import loads
from gnupg import GPG
from execution.semantic.transaction import Transaction, create_tx_from_json
from execution.utils import Event, send_message_to_node, BUFSIZE


def explore(data: dict, height: int, name: str, port: int, sock: socket, gpg: GPG) -> Transaction:
    send_message_to_node(data, Event.TRANSACTION_EXPLORE.value, name, port, sock, gpg)
    response = sock.recv(BUFSIZE)
    response_json = loads(response.decode())
    data = response_json["data"]
    block_json = data["transaction"]
    return create_tx_from_json(data["transaction"])


def explore_by_hash(_hash: str, node_name: str, node_port: int, sock: socket, gpg: GPG) -> Transaction:
    data = {"hash": _hash}
    return explore(data, Event.BLOCK_EXPLORE.value, node_name, node_port, sock, gpg)


if __name__ == "__main__":
    parser = ArgumentParser(description="Transactions explorer")
    parser.add_argument("node", metavar="<node>", help="Node name")
    parser.add_argument("port", metavar="<port>", help="Node port")
    parser.add_argument("--hash", nargs="?", help="transaction hash")
    args = parser.parse_args()
    sock = socket(AF_INET, SOCK_DGRAM)
    gpg = GPG()
    tx = None
    if args.hash is not None:
        tx = explore_by_hash(args.hash, args.node, int(args.port), sock, gpg)
    print(tx)
