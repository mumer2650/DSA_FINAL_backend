from typing import Optional
from .models import Property

class AVLNode:
    def __init__(self, property_obj : Property):
        self.price = property_obj.price
        # Store properties in a list to handle duplicates
        self.properties = [property_obj] 
        self.left: Optional[AVLNode] = None
        self.right: Optional[AVLNode] = None
        self.height = 1
    
def getHeight(root : AVLNode):
    if root == None: return 0
    
    return 1 + max(getHeight(root.left),getHeight(root.right))

def rightRotation(root: AVLNode):
    leftChild = root.left
    rightGrandChild = leftChild.right
    
    leftChild.right = root
    root.left = rightGrandChild
    
    return leftChild

def leftRotation(root: AVLNode):
    rightChild = root.right
    leftGrandChild = rightChild.left
    
    rightChild.left = root
    root.right = leftGrandChild
    
    return rightChild


class AVL_Tree_Property:
    def __init__(self):
        self.root: Optional[AVLNode] = None 
        self.size: int = 0
        
    def get_node_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_node_height(node.left) - self.get_node_height(node.right) if node else 0
        
    def rightRotation(self, root: AVLNode):
        leftChild = root.left
        rightGrandChild = leftChild.right
        

        leftChild.right = root
        root.left = rightGrandChild
        
        root.height = 1 + max(self.get_node_height(root.left), self.get_node_height(root.right))
        leftChild.height = 1 + max(self.get_node_height(leftChild.left), self.get_node_height(leftChild.right))
        

        return leftChild

    def leftRotation(self, root: AVLNode):
        rightChild = root.right
        leftGrandChild = rightChild.left
        
        rightChild.left = root
        root.right = leftGrandChild
        
        root.height = 1 + max(self.get_node_height(root.left), self.get_node_height(root.right))
        rightChild.height = 1 + max(self.get_node_height(rightChild.left), self.get_node_height(rightChild.right))
        
        return rightChild

    def insert(self, property_obj):
        self.root = self._insert_recursive(self.root, property_obj)
        self.size += 1

    def _insert_recursive(self, node, property_obj):
        if not node:
            return AVLNode(property_obj)
        
        if property_obj.price < node.price:
            node.left = self._insert_recursive(node.left, property_obj)
        elif property_obj.price > node.price:
            node.right = self._insert_recursive(node.right, property_obj)
        else:
            node.properties.append(property_obj)
            return node
        
        node.height = 1 + max(self.get_node_height(node.left), self.get_node_height(node.right))

        balance = self.get_balance(node)

        # Left Left Case
        if balance > 1 and property_obj.price < node.left.price:
            return self.rightRotation(node)
        # Right Right Case
        if balance < -1 and property_obj.price > node.right.price:
            return self.leftRotation(node)
        # Left Right Case
        if balance > 1 and property_obj.price > node.left.price:
            node.left = self.leftRotation(node.left)
            return self.rightRotation(node)
        # Right Left Case
        if balance < -1 and property_obj.price < node.right.price:
            node.right = self.rightRotation(node.right)
            return self.leftRotation(node)

        return node