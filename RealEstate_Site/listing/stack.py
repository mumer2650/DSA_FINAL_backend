class Stack:
    def __init__(self, max_size=10):
        self.items = []
        self.max_size = max_size

    def push(self, item):
        if item in self.items:
            self.items.remove(item)
        
        self.items.append(item)
        
        if len(self.items) > self.max_size:
            self.items.pop(0)

    def get_all(self):
        return list(reversed(self.items))

    def is_empty(self):
        return len(self.items) == 0