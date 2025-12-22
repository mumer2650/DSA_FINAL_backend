from typing import Optional
from .models import Property

class AVLNode:
    def __init__(self, property_obj : Property,balance_field : str):
        self.key = getattr(property_obj, balance_field)

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
    def __init__(self,ballance_field="price"):
        self.root: Optional[AVLNode] = None 
        self.size: int = 0
        self.balance_field = ballance_field
        
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

    def _insert_recursive(self, node, property_obj: Property):
        if not node:
            return AVLNode(property_obj,self.balance_field)
        
        new_val = getattr(property_obj, self.balance_field)
        
        if new_val < node.key:
            node.left = self._insert_recursive(node.left, property_obj)
        elif new_val > node.key:
            node.right = self._insert_recursive(node.right, property_obj)
        else:
            node.properties.append(property_obj)
            return node
        
        node.height = 1 + max(self.get_node_height(node.left), self.get_node_height(node.right))

        balance = self.get_balance(node)
        

        # Left Left Case
        if balance > 1 and new_val < node.left.key:
            return self.rightRotation(node)
        # Right Right Case
        if balance < -1 and new_val > node.right.key:
            return self.leftRotation(node)
        # Left Right Case
        if balance > 1 and new_val > node.left.key:
            node.left = self.leftRotation(node.left)
            return self.rightRotation(node)
        # Right Left Case
        if balance < -1 and new_val < node.right.key:
            node.right = self.rightRotation(node.right)
            return self.leftRotation(node)

        return node
    
    def get_all_sorted(self):
        sorted_list = []
        self._inorder_traversal(self.root, sorted_list)
        return sorted_list
    
    def _inorder_traversal(self, node: Optional[AVLNode], sorted_list: list):
        if node:
            self._inorder_traversal(node.left, sorted_list)
            
            for prop in node.properties:
                sorted_list.append(prop)
                
            self._inorder_traversal(node.right, sorted_list)
        
    def _preorder_traversal(self, node: Optional[AVLNode], _list: list):
        if node:
            for prop in node.properties:
                _list.append(prop)
            
            self._preorder_traversal(node.left, _list)
                
            self._preorder_traversal(node.right, _list)
            
    def search_by_price_range(self, min_price, max_price):
        search_results = []
        self._range_search_recursive(self.root, min_price, max_price, search_results)
        return search_results

    def _range_search_recursive(self, node, min_p, max_p, search_list):
        if node is None:
            return
        
        if node.key > min_p:
            self._range_search_recursive(node.left, min_p, max_p, search_list)

        if min_p <= node.key <= max_p:
            for p in node.properties:
                search_list.append(p)

        if node.key < max_p:
            self._range_search_recursive(node.right, min_p, max_p, search_list)      
            
                
property_tree = AVL_Tree_Property("price")
size_tree = AVL_Tree_Property("size")
