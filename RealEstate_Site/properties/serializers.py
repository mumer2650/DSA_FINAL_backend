from rest_framework import serializers
from .models import Property, Category
from maps.serializers import MapNodeSerializer

class CategorySerializer(serializers.ModelSerializer):
    # DSA TRICK: Recursive Serializer for Trees!
    # This field will look for 'subcategories' (children) and serialize them too.
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'subcategories']

    def get_subcategories(self, obj):
        # This function calls the serializer on itself recursively.
        # It allows us to output the entire tree structure in one JSON API call.
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.all(), many=True).data
        return []

class PropertySerializer(serializers.ModelSerializer):
    # Nested Serializer: Instead of just saying "Location ID: 5", 
    # it will give us the actual {x: 10, y: 20} data inside the property JSON.
    location_node = MapNodeSerializer(read_only=True)

    class Meta:
        model = Property
        fields = '__all__'  # A shortcut to include every field (price, area, title, etc.)