from typing import Optional
from .models import Location, Facility, Connection
from .queues import Queue
from .priority_queues import PriorityQueue
from listing.models import Property
from .utilis import calculate_haversine


class LocationGraph:
    def __init__(self):
        # Format: { location_id: [(neighbor_id, distance)] }
        self.adj_list = {}
        
        self.nodes_data = {}
           
    def add_location(self, location_obj : Location):
        if location_obj.id not in self.adj_list:
            facility_record = Facility.objects.filter(location=location_obj).first()
            category = facility_record.type if facility_record else ""
            
            
            display_name = facility_record.name if facility_record else location_obj.name
            
            self.adj_list[location_obj.id] = []
            self.nodes_data[location_obj.id] = {
                "name": display_name,
                "type": location_obj.location_type,
                "category": category   
            }
        
    def add_edge(self, loc_id1, loc_id2, distance):
        if loc_id1 not in self.adj_list: self.adj_list[loc_id1] = []
        if loc_id2 not in self.adj_list: self.adj_list[loc_id2] = []

        if not any(neighbor[0] == loc_id2 for neighbor in self.adj_list[loc_id1]):
            self.adj_list[loc_id1].append((loc_id2, distance))
            
        if not any(neighbor[0] == loc_id1 for neighbor in self.adj_list[loc_id2]):
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
            curr_dist, curr_id = pq.pop()
            
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
    
    def auto_connect_location(self,new_location, radius_km=15.0):
        other_locations = Location.objects.exclude(id=new_location.id)
        self.add_location(new_location)
        for other in other_locations:
            dist = calculate_haversine(
                new_location.latitude, new_location.longitude,
                other.latitude, other.longitude
            )
            
            if dist <= radius_km:
                Connection.objects.get_or_create(
                    from_location=new_location,
                    to_location=other,
                    defaults={'distance': dist}
                )
                Connection.objects.get_or_create(
                    from_location=other,
                    to_location=new_location,
                    defaults={'distance': dist}
                )
                self.add_edge(new_location.id,other.id,dist)
                self.add_edge(other.id,new_location.id,dist)
    

class RecomendationGraph:
    def __init__(self):
        # format  { prop_id : [(similar_prop_id,number_of_similarities)]}
        self.adj_list = {}
    
    def add_node(self,property_id):
        if property_id not in self.adj_list:
            self.adj_list[property_id] = []
        
    def add_edge(self,from_id,to_id,number_of_similarities):
        if from_id in self.adj_list and to_id in self.adj_list: 
            self.adj_list[from_id].append((to_id,number_of_similarities))
            self.adj_list[to_id].append((from_id,number_of_similarities))
            
    def generate_similarity_graph(self,property_obj):
        for prop1 in property_obj:
            for prop2 in property_obj:
                
                if prop1.id == prop2.id:
                    continue
                    
                similarities = 0
                if abs(prop1.price - prop2.price) / prop1.price <= 0.30: similarities += 1
                if abs(prop1.size - prop2.size) / prop1.size <= 0.30: similarities += 1
                
                if similarities >= 1:
                    self.add_node(prop1.id)
                    self.add_node(prop2.id)
                    self.add_edge(prop1.id,prop2.id,similarities)
        return self.adj_list

    def bfs_traversal(self,start_node):
        q = Queue()
        visited = set()
        q.enqueue(start_node)
        visited.add(start_node)
        all_recommendations = []
        
        while not q.is_empty():
            curr_id = q.dequeue()
        
            neighbors = self.adj_list.get(curr_id, [])
            
            for neighbor_id, score in neighbors:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    
                    all_recommendations.append((neighbor_id, score))
                    q.enqueue(neighbor_id)
        
        return [item[0] for item in all_recommendations]
            
        
                


graph = LocationGraph()