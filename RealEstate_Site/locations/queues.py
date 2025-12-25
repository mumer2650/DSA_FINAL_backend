
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class Queue:
    def __init__(self):
        self.front = None
        self.rear = None
        self.size = 0

    def is_empty(self):
        return self.front is None

    def enqueue(self, item):

        new_node = Node(item)
        if self.rear is None:
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self.size += 1

    def dequeue(self):
        if self.is_empty():
            return None
        
        temp = self.front
        self.front = self.front.next
        
        if self.front is None:
            self.rear = None
            
        self.size -= 1
        return temp.data

    def get_size(self):
        return self.size
    
q = Queue()