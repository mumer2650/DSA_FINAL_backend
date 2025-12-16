from django.db import models

class MapNode(models.Model):
    # These are the choices for what a node can be
    NODE_TYPES = (
        ('INTERSECTION', 'Road Intersection'),
        ('HOUSE', 'Property Location'),
        ('AMENITY', 'Amenity (School/Hospital)'),
    )

    # x and y are the coordinates on your 2D grid
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    
    # What kind of node is this?
    node_type = models.CharField(max_length=20, choices=NODE_TYPES, default='INTERSECTION')
    
    # Name is optional, e.g., "Main St. Junction" or "City Hospital"
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name or 'Node'} ({self.x_coordinate}, {self.y_coordinate})"

class RoadSegment(models.Model):
    # This represents the "Edge" in your graph
    start_node = models.ForeignKey(MapNode, on_delete=models.CASCADE, related_name='outgoing_roads')
    end_node = models.ForeignKey(MapNode, on_delete=models.CASCADE, related_name='incoming_roads')
    
    # Weight of the edge (distance)
    distance = models.FloatField(help_text="Distance in meters or grid units")
    
    def __str__(self):
        return f"Road from {self.start_node} to {self.end_node}"