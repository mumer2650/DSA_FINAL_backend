from rest_framework import serializers
from .models import HomeLayout, Room


class RoomSerializer(serializers.ModelSerializer):
    """
    Serializer for individual rooms in a house layout.
    """
    adj = serializers.SerializerMethodField()
    type = serializers.CharField(source='room_type', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'type', 'floor', 'x', 'y', 'width', 'height', 'adj']

    def get_adj(self, obj):
        """
        Get adjacent room IDs for this room.
        """
        # This will be populated by the view/service layer
        # as we need the full graph to determine adjacency
        return getattr(obj, 'adjacent_rooms', [])


class HomeLayoutSerializer(serializers.ModelSerializer):
    """
    Serializer for complete home layouts with rooms.
    """
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = HomeLayout
        fields = ['id', 'length', 'width', 'floors', 'request_payload', 'created_at', 'rooms']


class LayoutRequestSerializer(serializers.Serializer):
    """
    Serializer for layout generation request.
    """
    length = serializers.FloatField(min_value=30, max_value=100)  # meters
    width = serializers.FloatField(min_value=40, max_value=100)   # meters
    floors = serializers.IntegerField(min_value=1, max_value=5)   # allow up to 5 floors
    rooms = serializers.IntegerField(min_value=2, max_value=24)   # total rooms in entire house
    minRoomLength = serializers.FloatField(min_value=5, max_value=50, default=15)  # meters
    minRoomWidth = serializers.FloatField(min_value=5, max_value=50, default=15)   # meters
    kitchenSize = serializers.FloatField(min_value=10, max_value=500, default=280)  # square meters
    totalBedrooms = serializers.IntegerField(min_value=1, max_value=10, default=4)  # total ATTACHED_BED_BATH units

    def validate(self, data):
        """
        Validate request data.
        """
        # Validate that room dimensions make sense
        min_length = data.get('minRoomLength', 20)
        min_width = data.get('minRoomWidth', 25)

        if min_length <= 0 or min_width <= 0:
            raise serializers.ValidationError("Room dimensions must be positive")

        # House width must be between 40 and 100 metres
        if not (40 <= data['width'] <= 100):
            raise serializers.ValidationError("Width must be between 40 and 100 metres")

        # House length (depth) must be in [0.75 * width, width]
        min_length = 0.75 * data['width']
        if not (min_length <= data['length'] <= data['width']):
            raise serializers.ValidationError(f"Length (depth) must be between 0.75 * width ({min_length}) and width ({data['width']})")

        # Basic validation for kitchen and bedroom requirements
        if data['totalBedrooms'] <= 0:
            raise serializers.ValidationError("Total bedrooms must be positive")

        # Kitchen should be reasonably sized
        if data['kitchenSize'] <= 0:
            raise serializers.ValidationError("Kitchen size must be positive")

        return data


class LayoutResponseSerializer(serializers.Serializer):
    """
    Serializer for layout generation response.
    """
    home_id = serializers.IntegerField()
    request_payload = serializers.DictField()
    rooms = serializers.ListField(child=serializers.DictField())

    def to_representation(self, instance):
        """
        Convert HomeLayout instance to response format.
        """
        if isinstance(instance, HomeLayout):
            rooms_data = []
            for room in instance.rooms.all():
                room_dict = {
                    'id': room.id,
                    'type': room.room_type,
                    'floor': room.floor,
                    'x': room.x,
                    'y': room.y,
                    'width': room.width,
                    'height': room.height,
                    'adj': getattr(room, 'adjacent_rooms', [])
                }
                rooms_data.append(room_dict)

            return {
                'home_id': instance.id,
                'request_payload': instance.request_payload,
                'rooms': rooms_data
            }

        return super().to_representation(instance)


class UserLayoutsSerializer(serializers.Serializer):
    """
    Serializer for user's layout list response.
    """
    layouts = HomeLayoutSerializer(many=True)