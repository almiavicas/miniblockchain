import os
from typing import List, Dict, Any
from socket import socket
from enum import Enum
from json import dumps
from gnupg import GPG
from datetime import datetime

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


class Log:
    def __init__(self, dt_str: str, name: str, message: str):
        self.dt_str = dt_str
        self.dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S,%f")
        self.name = name
        self.message = message


    def __lt__(self, o):
        result = self.dt < o.dt
        result = result or self.dt == o.dt and self.name < o.name
        result = result or self.dt == o.dt and self.name == o.name and self.message < o.message
        return result

    
    def __str__(self):
        return f"{self.dt_str} | {self.name}: {self.message}"


def parse_log_file(filename: str) -> List[Log]:
    logs = []
    with open(filename, encoding="utf-8") as _file:
        for line in _file.readlines():
            time, log_event = line.split('|')
            name, message = log_event.strip().split(':', 1)
            log = Log(time.strip(), name.strip(), message.strip())
            logs.append(log)
    return logs


class LogFile:
    def __init__(self, filename: str):
        self.filename = filename
        self.logs = parse_log_file(filename)


    def find_logs_by_substr(self, substrs: List[str]) -> List[Log]:
        logs: List[Log] = []
        for log in self.logs:
            if any(substr in log.message for substr in substrs):
                logs.append(log)
        return logs


class LogService:

    ALL_EVENTS = [
        str(Event.PRESENTATION),
        str(Event.PRESENTATION_ACK),
        str(Event.NEW_TRANSACTION),
        str(Event.NEW_TRANSACTION_ACK),
        str(Event.TRANSACTION),
        str(Event.TRANSACTION_ACK),
        str(Event.BLOCK),
        str(Event.BLOCK_ACK),
        str(Event.BLOCK_EXPLORE),
        str(Event.BLOCK_EXPLORE_ACK),
        str(Event.TRANSACTION_EXPLORE),
        str(Event.TRANSACTION_EXPLORE_ACK),
    ]
    TRANSACTION_EVENTS = [
        str(Event.NEW_TRANSACTION),
        str(Event.NEW_TRANSACTION_ACK),
        str(Event.TRANSACTION),
        str(Event.TRANSACTION_ACK),
        str(Event.TRANSACTION_EXPLORE),
        str(Event.TRANSACTION_EXPLORE_ACK),
    ]
    BLOCK_EVENTS = [
        str(Event.BLOCK),
        str(Event.BLOCK_ACK),
        str(Event.BLOCK_EXPLORE),
        str(Event.BLOCK_EXPLORE_ACK),
    ]


    def __init__(self, logs_dir: str):
        self.log_files: Dict[str, LogFile] = {}
        self.log_start: datetime = None
        self.log_end: datetime = None
        for filename in os.listdir(logs_dir):
            log_file = LogFile(f"{logs_dir}/{filename}")
            first_log_dt = log_file.logs[0].dt
            if self.log_start is None or first_log_dt < self.log_start:
                self.log_start = first_log_dt
            last_log_dt = log_file.logs[-1].dt
            if self.log_end is None or last_log_dt > self.log_end:
                self.log_end = last_log_dt
            self.log_files[log_file.filename] = log_file
        


    def compose_logs(self) -> List[Log]:
        """Return a unique dict with the logs of every logfile."""
        composed_logs: List[Log] = []
        for log_file in self.log_files.values():
            composed_logs += log_file.logs
        return sorted(composed_logs)


    def find_logs_by_timestamp_range(self, start: datetime, end: datetime) -> Dict[str, List[Log]]:
        log_files: Dict[str, List[Log]] = {}
        for log_file in self.log_files.values():
            start_index = 0
            while start_index < len(log_file.logs) and log_file.logs[start_index].dt < start:
                start_index += 1
            end_index = len(log_file.logs) - 1
            while end_index > 0 and log_file.logs[end_index].dt > end:
                end_index -= 1
            log_files[log_file.filename] = log_file.logs[start_index:end_index]
        return log_files

    
    def find_logs_by_op_type(self, op_type: str) -> Dict[str, List[Log]]:
        log_files: Dict[str, List[Log]] = {}
        event_strs = None
        if op_type == "all":
            event_strs = self.ALL_EVENTS
        elif op_type == "transaction":
            event_strs = self.TRANSACTION_EVENTS
        elif op_type == "block":
            event_strs = self.BLOCK_EVENTS
        for log_file in self.log_files.values():
            logs = log_file.find_logs_by_substr(event_strs)
            log_files[log_file.filename] = logs
        return log_files

    
    def find_logs_by_op(self, op: str) -> Dict[str, List[Log]]:
        log_files: Dict[str, List[Log]] = {}
        event_strs = [op]
        for log_file in self.log_files.values():
            logs = log_file.find_logs_by_substr(event_strs)
            log_files[log_file.filename] = logs
        return log_files


    def log_names(self) -> tuple:
        names = ()
        for log_file in self.log_files.values():
            names += log_file.logs[0].name,
        return tuple(sorted(names))


    def __iter__(self):
        return iter(self.compose_logs())
