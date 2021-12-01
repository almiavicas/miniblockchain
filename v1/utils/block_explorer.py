from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_DGRAM
from json import loads
from gnupg import GPG
from execution.semantic.block import Block, create_block_from_json
from execution.utils import Event, send_message_to_node, BUFSIZE


def explore(data: dict, height: int, name: str, port: int, sock: socket, gpg: GPG) -> Block:
    send_message_to_node(data, Event.BLOCK_EXPLORE.value, name, port, sock, gpg)
    response = sock.recv(BUFSIZE)
    response_json = loads(response.decode())
    data = response_json["data"]
    return create_block_from_json(data["block"]) if data["block"] is not None else None


def explore_by_height(height: int, node_name: str, node_port: int, sock: socket, gpg: GPG) -> Block:
    data = {"height": height}
    return explore(data, Event.BLOCK_EXPLORE.value, node_name, node_port, sock, gpg)


def explore_by_hash(_hash: str, node_name: str, node_port: int, sock: socket, gpg: GPG) -> Block:
    data = {"hash": _hash}
    return explore(data, Event.BLOCK_EXPLORE.value, node_name, node_port, sock, gpg)


if __name__ == "__main__":
    parser = ArgumentParser(description="Blocks explorer")
    parser.add_argument("node", metavar="<node>", help="Node name")
    parser.add_argument("port", metavar="<port>", help="Node port")
    parser.add_argument("--hash", nargs="?", help="block hash")
    parser.add_argument("--height", nargs="?", help="block height")
    args = parser.parse_args()
    sock = socket(AF_INET, SOCK_DGRAM)
    gpg = GPG()
    block = None
    if args.hash is not None:
        block = explore_by_hash(args.hash, args.node, int(args.port), sock, gpg)
    elif args.height is not None:
        block = explore_by_height(int(args.height), args.node, int(args.port), sock, gpg)
    print(block)
