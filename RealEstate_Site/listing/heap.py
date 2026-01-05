from typing import Optional
from .models import Property

class CheapPropertyHeap:
    """
    Min-heap for properties ordered by price.
    Format: [(price, property_obj), ...]
    """
    def __init__(self):
        self.heap  = []

    def insert(self, property_obj: Property):
        self.heap.append((property_obj.price, property_obj))
        self.heapify_up(len(self.heap) - 1)

    def extract_min(self):
        if len(self.heap) == 0:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self.heapify_down(0)
        return root
    
    def remove_by_id(self, property_id):
        for i in range(len(self.heap)):
            if self.heap[i][1].id == property_id:
                self.heap[i] = self.heap[-1]
                self.heap.pop()
                if i < len(self.heap):
                    self.heapify_down(i)
                    self.heapify_up(i)
                return True
        return False

    def update_property(self, old_id, new_property_obj):
        self.remove_by_id(old_id)
        self.insert(new_property_obj)

    def heapify_up(self, index):
        parent = (index - 1) // 2
        if index > 0 and self.heap[index][0] < self.heap[parent][0]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self.heapify_up(parent)

    def heapify_down(self, index):
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2

        if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:
            smallest = left
        if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right

        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self.heapify_down(smallest)

    def __len__(self):
        return len(self.heap)
    
class LargestPropertyHeap:
    """
    Max-heap for properties ordered by size.
    Format: [(size, property_obj), ...]
    """
    def __init__(self):
        self.heap = []

    def insert(self, property_obj):
        self.heap.append((property_obj.size, property_obj))
        self.heapify_up(len(self.heap) - 1)

    def extract_max(self):
        if len(self.heap) == 0:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self.heapify_down(0)
        return root
    
    def remove_by_id(self, property_id):
        for i in range(len(self.heap)):
            if self.heap[i][1].id == property_id:
                self.heap[i] = self.heap[-1]
                self.heap.pop()
                if i < len(self.heap):
                    self.heapify_down(i)
                    self.heapify_up(i)
                return True
        return False

    def update_property(self, old_id, new_property_obj):
        self.remove_by_id(old_id)
        self.insert(new_property_obj)

    def heapify_up(self, index):
        parent = (index - 1) // 2
        if index > 0 and self.heap[index][0] > self.heap[parent][0]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self.heapify_up(parent)

    def heapify_down(self, index):
        largest = index
        left = 2 * index + 1
        right = 2 * index + 2

        if left < len(self.heap) and self.heap[left][0] > self.heap[largest][0]:
            largest = left
        if right < len(self.heap) and self.heap[right][0] > self.heap[largest][0]:
            largest = right

        if largest != index:
            self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
            self.heapify_down(largest)

    def __len__(self):
        return len(self.heap)
    
    
cheap_heap = CheapPropertyHeap()
size_heap = LargestPropertyHeap()