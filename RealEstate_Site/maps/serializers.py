from rest_framework import serializers
from .models import MapNode, RoadSegment

class MapNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapNode
        fields = ['id', 'x_coordinate', 'y_coordinate', 'node_type', 'name']

class RoadSegmentSerializer(serializers.ModelSerializer):
    # We keep it simple: Start ID -> End ID. 
    # This allows Dijkstra's algorithm to easily build an "Adjacency Matrix".
    class Meta:
        model = RoadSegment
        fields = ['id', 'start_node', 'end_node', 'distance', 'road_name']