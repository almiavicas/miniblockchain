import os
from typing import List, Dict, Any
from collections import namedtuple
from socket import socket
from enum import Enum
from json import dumps
from gnupg import GPG
from datetime import datetime
from collections import OrderedDict

LOCALHOST = "127.0.0.1"
BUFSIZE = 2**13

Event = Enum(
    "Event",
    (
        "PRESENTATION",
        "PRESENTATION_ACK",
        "NEW_TRANSACTION",
        "NEW_TRANSACTION_ACK",
        "TRANSACTION",
        "TRANSACTION_ACK",
        "BLOCK",
        "BLOCK_ACK",
        "BLOCK_EXPLORE",
        "BLOCK_EXPLORE_ACK",
        "TRANSACTION_EXPLORE",
        "TRANSACTION_EXPLORE_ACK",
        "LOG_DIR",
    )
)

def create_dir(dirname: str):
    directory = os.path.dirname(dirname)
    try:
        os.stat(directory)
    except:
        print("Creating directory", directory)
        os.mkdir(directory)

def parse_network_file(filename: str) -> Dict[str, Any]:
    ports_info = {}
    neighbors_info = {}
    with open(filename, encoding="utf-8") as _file:
        n = int(_file.readline())
        for i in range(0, n):
            node, port = _file.readline().split()
            ports_info[node] = int(port)
            neighbors_info[node] = []
        m = int(_file.readline())
        for i in range(0, m):
            node1, node2 = _file.readline().split()
            neighbors_info[node1].append(node2)
            neighbors_info[node2].append(node1)
    return {
        "ports_info": ports_info,
        "neighbors_info": neighbors_info,
    }

def parse_config_file(filename: str) -> dict:
    config = {}
    with open(filename, encoding="utf-8") as _file:
        for line in _file.readlines():
            key, value = line.split()
            config[key[:-1].lower()] = int(value)
    return config

def parse_log_file(filename: str, logs: OrderedDict, nodo_name: str) -> dict:
    config = {}
    with open(filename, encoding="utf-8") as _file:
        for line in _file.readlines():
            time, log_event = line.split('|')
            timeParser = datetime.strptime(time.strip(), "%Y-%m-%d %H:%M:%S,%f")
            nodo, log = log_event.strip().split(':', 1)
            logs[timeParser] = {
                'nodo': nodo,
                'log_event': log
            }
    return config

def get_gpg() -> GPG:
    homedir = os.environ.get("HOME", None)
    if homedir is None:
        raise Exception("You must set the HOME environment variable to the parent of the .gnupg folder")
    gnupghome = f"{homedir}/.gnupg"
    try:
        return GPG(gnupghome=gnupghome) 
    except TypeError:
        return GPG(homedir=gnupghome)

def get_fingerprints(gpg: GPG, prefix=None) -> Dict[str, str]:
    """Get a dict of fingerprints from gnupg linked to one of their uids"""
    keys = gpg.list_keys()
    fingerprints = {}
    for key in keys:
        for uid in key["uids"]:
            if prefix is not None:
                if uid.startswith(prefix):
                    fingerprints[uid] = key["fingerprint"]
                    break
            else:
                fingerprints[uid] = key["fingerprint"]
                break
    return fingerprints


def send_message_to_node(data: dict, event: int, name: str, port: int, sock: socket, gpg: GPG):
    message = dumps({
        "event": event,
        "data": data,
    })
    encrypted_message = gpg.encrypt(message, name, armor=False)
    if not encrypted_message.ok:
        raise Exception("Encryption failed with status %s" % encrypted_message.status)
    sock.sendto(str(encrypted_message).encode(), (LOCALHOST, port))
