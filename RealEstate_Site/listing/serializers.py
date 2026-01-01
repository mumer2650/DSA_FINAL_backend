from rest_framework import serializers
from .models import Property , PropertyRequest, SellPropertyDetail
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
            'latitude', 'longitude',
            'is_featured'
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
    
    # --- THE FIX IS HERE ---
    def to_representation(self, instance):
        """
        This ensures that when we GET properties, we actually see the coordinates
        stored in the related Location object.
        """
        representation = super().to_representation(instance)
        
        # Manually inject the location data from the relation
        if instance.location_id:
            representation['latitude'] = instance.location_id.latitude
            representation['longitude'] = instance.location_id.longitude
            representation['location_name'] = instance.location_id.name
            
        return representation
    

class SellPropertyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellPropertyDetail
        fields = ['id', 'title', 'location_name', 'latitude', 'longitude', 'price']

class PropertyRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    sell_prop = SellPropertyDetailSerializer(read_only=True)

    class Meta:
        model = PropertyRequest
        fields = [
            'id', 'user_name', 'property', 'sell_prop', 
            'request_type', 'status', 'created_at'
        ]
        read_only_fields = ['user', 'status', 'created_at']

    def to_representation(self, instance):
        """
        When reading data, we swap the simple Property ID for the FULL Property Object.
        This allows the frontend to have instant access to images/prices without extra API calls.
        """
        response = super().to_representation(instance)
        
        # If this is a BUY request (and has a property linked), serialize the full object
        if instance.request_type == 'buy' and instance.property:
            response['property'] = PropertySerializer(instance.property).data
            
        return response