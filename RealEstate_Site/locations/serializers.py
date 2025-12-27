from rest_framework import serializers
from .models import Location, Facility, Connection

class FacilitySerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Facility
        fields = ['id', 'name', 'location', 'type_display']

class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude', 'location_type']

class ConnectionSerializer(serializers.ModelSerializer):
    from_location_name = serializers.ReadOnlyField(source='from_location.name')
    to_location_name = serializers.ReadOnlyField(source='to_location.name')

    class Meta:
        model = Connection
        fields = ['id', 'from_location', 'from_location_name', 'to_location', 'to_location_name', 'distance']