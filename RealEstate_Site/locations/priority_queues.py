from .min_heap import MinHeap

class PriorityQueue:
    def __init__(self):
        self.min_heap = MinHeap()

    def is_empty(self):
        return len(self.min_heap) == 0

    def push(self, node_id, distance):
        self.min_heap.insert((distance, node_id))

    def pop(self):
        result = self.min_heap.extract_min()
        if result:
            return result[1], result[0]
        return None