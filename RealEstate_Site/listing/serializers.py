from rest_framework import serializers
from .models import Property
from locations.models import Location

class PropertySerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(write_only=True)
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'price', 'area', 'size', 'bedrooms', 
            'bathrooms', 'image', 'location_name', 'latitude', 'longitude'
        ]
        
    def create(self, validated_data):
        loc_name = validated_data.pop('location_name')
        lat = validated_data.pop('latitude')
        lon = validated_data.pop('longitude')
        title = validated_data.get('title')
        loc_type = "property"

        location_obj, created = Location.objects.get_or_create(
            name=loc_name,
            defaults={'latitude': lat, 'longitude': lon, 'location_type': loc_type}
        )
        
        exists = Property.objects.filter(location_id=location_obj, title=title).exists()
        
        if exists:
            raise serializers.ValidationError({
                "detail": "This property listing already exists at this location!"
            })

        property_obj = Property.objects.create(location_id=location_obj, **validated_data)
        return property_obj