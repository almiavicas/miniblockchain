from socket import socket
from typing import Dict, List
from json import dumps
from gnupg import GPG
from utils import LOCALHOST

class Neighbor:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.is_active = False

    def send_message(self, sock: socket, event: int, data: str, gpg: GPG):
        # The armor=False argument is to get the message as binary data. This is useful
        # when we want to decrypt the message, because gpg decrypts by default a binary-like
        # object.
        # encrypted_message = gpg.encrypt(message, self.name, armor=False)
        # We get an Encript object from this. To check if the encryption succedded, we can
        # check if the encrypted_message.ok is True.
        # if not encrypted_message.ok:
            # raise Exception("gpg could not encrypt the message `%s`" % message)
        # To get the encrypted data we need to convert the object to a string.
        # bynary_data = str(encrypted_message)
        message = dumps({
            "event": event,
            "data": data,
        })
        address = (LOCALHOST, self.port)
        sock.sendto(message.encode(), address)

    def __str__(self):
        return f"{self.name}: {self.port} ({'IN' if not self.is_active else ''}ACTIVE)"

def create_neighbors(ports_config: dict, neighbor_names: List[str], node: str) -> Dict[str, Neighbor]:
    """Create a dict of Neighbors for a given node with the specified ports config"""
    neighbor_nodes = {}
    for name in neighbor_names:
        neighbor_nodes[name] = Neighbor(name, ports_config[name])
    return neighbor_nodes