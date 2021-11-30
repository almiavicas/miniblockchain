from socket import socket
from typing import Dict, List
from json import dumps
from gnupg import GPG
from utils import send_message_to_node

class Neighbor:
    def __init__(self, name: str, port: int, fingerprint: str):
        self.name = name
        self.port = port
        self.fingerprint = fingerprint
        self.is_active = False


    def send_message(self, sock: socket, event: int, data: dict, gpg: GPG):
        send_message_to_node(data, event, self.name, self.port, sock, gpg)


    def __str__(self):
        return f"{self.name}: {self.port} ({'IN' if not self.is_active else ''}ACTIVE)"


def create_neighbors(
    ports_config: dict,
    neighbor_names: List[str],
    fingerprints: Dict[str, str]
) -> Dict[str, Neighbor]:
    """Create a dict of Neighbors for a given node with the specified ports config"""
    neighbor_nodes = {}
    for name in neighbor_names:
        try:
            neighbor_nodes[name] = Neighbor(name, ports_config[name], fingerprints[name])
        except KeyError as e:
            raise Exception("Fingerprint for %s not found" % name) from e
    return neighbor_nodes