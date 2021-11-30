from socket import socket
from json import loads
from gnupg import GPG
from execution.semantic.block import Block, create_block_from_json
from execution.utils import Event, send_message_to_node, BUFSIZE


def parse_response(response: bytes) -> Block:
    response_json = loads(response.decode())
    data = response_json["data"]
    block_json = data["block"]
    return create_block_from_json(data["block"])


def explore_by_height(height: int, node_name: str, node_port: int, sock: socket, gpg: GPG) -> Block:
    data = {"height": height}
    send_message_to_node(data, Event.BLOCK_EXPLORE.value, node_name, node_port, sock, gpg)
    response = sock.recv(BUFSIZE)
    return parse_response(response)
