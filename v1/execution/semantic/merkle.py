from hashlib import sha256
from typing import List
from .transaction import Transaction

class Node:
    def __init__(self, left, right, value, content)-> None:
        self.left: Node = left
        self.right: Node = right
        self.value = value
        self.content = content
    
    @staticmethod
    def hash(val):
        return sha256(str(val).encode('utf-8')).hexdigest()

    def __str__(self):
      return (str(self.value))
 
class MerkleTree:
    def __init__(self, values: List[str])-> None:
        self.root = Node(None, None, Node.hash('root'),'root')
        self.__buildTree(values)
 
    def __buildTree(self, values: List[str])-> None:
        if len(values) == 0:
            return
        leaves: List[Node] = [Node(None, None, Node.hash(e),e) for e in values]
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1:][0]) # duplicate last elem if odd number of elements
        self.root: Node = self.__buildTreeRec(leaves) 
    
    def __buildTreeRec(self, nodes: List[Node])-> Node:
        half: int = len(nodes) // 2
 
        if len(nodes) == 2:
            return Node(nodes[0], nodes[1], Node.hash(nodes[0].value + nodes[1].value), str(nodes[0].content)+"+"+str(nodes[1].content))
        elif len(nodes) == 1:
            return nodes[0]

        left_nodes_set = nodes[:half]
        right_nodes_set = nodes[half:]
        left: Node = self.__buildTreeRec(left_nodes_set)
        right: Node = self.__buildTreeRec(right_nodes_set)
        value: str = Node.hash(left.value + right.value)
        content: str = str(self.__buildTreeRec(left_nodes_set).content)+"+"+str(self.__buildTreeRec(right_nodes_set).content)
        
        return Node(left, right, value,content)
    
    def getRootHash(self)-> str:
        return self.root.value
        