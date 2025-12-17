from rest_framework import serializers
from .models import LayoutRequest, GeneratedBlueprint

class GeneratedBlueprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedBlueprint
        fields = ['id', 'structure_json', 'created_at']

class LayoutRequestSerializer(serializers.ModelSerializer):
    # We include the blueprint here so if a request has a result, we see it.
    blueprint = GeneratedBlueprintSerializer(read_only=True)

    class Meta:
        model = LayoutRequest
        fields = ['id', 'name', 'plot_width', 'plot_length', 
                  'min_room_size', 'complexity_level', 'blueprint']