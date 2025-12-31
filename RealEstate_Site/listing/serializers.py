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
            'id', 'title', 'price',  'size', 'bedrooms', 
            'bathrooms','floors', 'kitchens', 'description', 'image', 'location_id', 'location_name', 
            'latitude', 'longitude'
        ]
        extra_kwargs = {
            'location_id': {'read_only': True}
        }
        
    def create(self, validated_data):
        loc_name = validated_data.pop('location_name')
        lat = validated_data.pop('latitude')
        lon = validated_data.pop('longitude')
        
        location_obj, created = Location.objects.get_or_create(
            latitude=lat,
            longitude=lon,
            defaults={'name': loc_name, 'location_type': "property"}
        )

        title = validated_data.get('title')

        if Property.objects.filter(location_id=location_obj, title=title).exists():
            raise serializers.ValidationError("This property listing already exists at this exact location!")

        property_obj = Property.objects.create(location_id=location_obj, **validated_data)
        
        return property_obj