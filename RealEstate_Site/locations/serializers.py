from rest_framework import serializers
from .models import Location, Facility, Connection, WayPoint

class FacilitySerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Facility
        fields = ['id', 'name', 'location', 'type_display']

class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude', 'location_type']
        
class WayPointSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='location.name')
    latitude = serializers.ReadOnlyField(source='location.latitude')
    longitude = serializers.ReadOnlyField(source='location.longitude')
    node_type_display = serializers.CharField(source='get_node_type_display', read_only=True)

    class Meta:
        model = WayPoint
        fields = [
            'id',        
            'name',            
            'node_type',       
            'node_type_display',
            'latitude', 
            'longitude'
            'location'
        ]
class ConnectionSerializer(serializers.ModelSerializer):
    from_location_name = serializers.ReadOnlyField(source='from_location.name')
    to_location_name = serializers.ReadOnlyField(source='to_location.name')

    class Meta:
        model = Connection
        fields = ['id', 'from_location', 'from_location_name', 'to_location', 'to_location_name', 'distance']
        
class ConnectionBulkSerializer(serializers.ModelSerializer):
    from_location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    to_location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())

    class Meta:
        model = Connection
        fields = ['from_location', 'to_location']