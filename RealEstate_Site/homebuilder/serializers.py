from rest_framework import serializers
from .models import HomeLayout, Room


class RoomSerializer(serializers.ModelSerializer):
    """
    Serializer for individual rooms in a house layout.
    """
    adj = serializers.SerializerMethodField()

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
        fields = ['id', 'length', 'width', 'floors', 'created_at', 'rooms']


class LayoutRequestSerializer(serializers.Serializer):
    """
    Serializer for layout generation request.
    """
    length = serializers.FloatField(min_value=10, max_value=200)  # meters
    width = serializers.FloatField(min_value=10, max_value=200)   # meters
    floors = serializers.IntegerField(min_value=1, max_value=5)   # allow up to 5 floors
    rooms = serializers.IntegerField(min_value=3, max_value=20)   # rooms per floor
    minRoomLength = serializers.FloatField(min_value=5, max_value=50, default=20)  # meters
    minRoomWidth = serializers.FloatField(min_value=5, max_value=50, default=25)   # meters
    kitchenSize = serializers.FloatField(min_value=10, max_value=500, default=250)  # square meters
    washroomSize = serializers.FloatField(min_value=5, max_value=200, default=100)  # square meters

    def validate(self, data):
        """
        Validate request data.
        """
        # Validate that room dimensions make sense
        min_length = data.get('minRoomLength', 20)
        min_width = data.get('minRoomWidth', 25)

        if min_length <= 0 or min_width <= 0:
            raise serializers.ValidationError("Room dimensions must be positive")

        # Basic sanity check - house should be reasonably sized
        if data['length'] < data['width']:
            raise serializers.ValidationError("House length should typically be greater than or equal to width")

        # Kitchen should be reasonably sized compared to room minimums
        min_room_area = min_length * min_width
        if data['kitchenSize'] < min_room_area * 0.8:
            raise serializers.ValidationError("Kitchen size should be at least 80% of minimum room area")

        return data


class LayoutResponseSerializer(serializers.Serializer):
    """
    Serializer for layout generation response.
    """
    home_id = serializers.IntegerField()
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
                'rooms': rooms_data
            }

        return super().to_representation(instance)


class UserLayoutsSerializer(serializers.Serializer):
    """
    Serializer for user's layout list response.
    """
    layouts = HomeLayoutSerializer(many=True)