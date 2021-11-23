import os
from gnupg import GPG


def create_dir(dirname: str):
    directory = os.path.dirname(dirname)
    try:
        os.stat(directory)
    except:
        print("Creating directory", directory)
        os.mkdir(directory)

def parse_network_file(filename: str) -> dict:
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

def get_gpg():
    homedir = os.environ.get("HOME", None)
    if homedir is None:
        print("You must set the HOME environment variable to the parent of the .gnupg folder")
    gnupghome = f"{homedir}/.gnupg"
    return GPG(gnupghome=gnupghome)
