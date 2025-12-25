from typing import Optional
from .models import Location, Facility
from .queues import Queue
from .priority_queues import PriorityQueue


class LocationGraph:
    def __init__(self):
        # Format: { location_id: [(neighbor_id, distance)] }
        self.adj_list = {}
        
        self.nodes_data = {}
        
        
    def add_location(self, location_obj : Location):
        if location_obj.id not in self.adj_list:
            facility_record = Facility.objects.filter(location=location_obj).first()
            category = facility_record.type if facility_record else ""
            
            self.adj_list[location_obj.id] = []
            self.nodes_data[location_obj.id] = {
                "name": location_obj.name,
                "type": location_obj.location_type,
                "category": category   
            }
        
    def add_edge(self, loc_id1, loc_id2, distance):
        if loc_id1 in self.adj_list and loc_id2 in self.adj_list: 
            self.adj_list[loc_id1].append((loc_id2, distance))
            self.adj_list[loc_id2].append((loc_id1, distance))
            
    def bfs_nearby_facilities(self, start_id, max_distance):
        q = Queue() 
        q.enqueue((start_id, 0))
        
        visited = set()
        found_facilities = [] 

        while not q.is_empty():
            curr_id, current_total_dist = q.dequeue()
            
            if curr_id in visited:
                continue
            
            visited.add(curr_id)
            
            if self.nodes_data[curr_id]['type'] == 'facility' and curr_id != start_id:
                found_facilities.append({
                    "id": curr_id,
                    "name": self.nodes_data[curr_id]['name'],
                    "distance": current_total_dist,
                    "category" : self.nodes_data[curr_id]['category']
                })

            for neighbor_id, weight in self.adj_list.get(curr_id, []):
                new_dist = current_total_dist + weight
                
                if neighbor_id not in visited and new_dist <= max_distance:
                    q.enqueue((neighbor_id, new_dist))
        
        return found_facilities
    
    def dijkstra_shortest_path(self, from_id, to_id):
        pq = PriorityQueue()
        pq.push(0,from_id) 

        distances = {node: float('inf') for node in self.adj_list}
        distances[from_id] = 0
        
        parent = {node: None for node in self.adj_list}
        
        visited = set()

        while not pq.is_empty():
            curr_id, curr_dist = pq.pop()
            
            if curr_id == to_id:
                return round(curr_dist, 2)

            if curr_id in visited:
                continue
            visited.add(curr_id)

            for neighbor_id, weight in self.adj_list.get(curr_id, []):
                if neighbor_id in visited:
                    continue
                    
                new_dist = curr_dist + weight
                
                if new_dist < distances[neighbor_id]:
                    distances[neighbor_id] = new_dist
                    parent[neighbor_id] = curr_id
                    pq.push(new_dist,neighbor_id)

        return float("inf")


graph = LocationGraph()