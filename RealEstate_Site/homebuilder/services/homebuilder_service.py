from django.db import transaction
from ..models import HomeLayout, Room
from .bsp import generate_house
from .room_graph import build_connectivity_graph
from .validator import comprehensive_validation

class HomeBuilderService:
    MAX_REGENERATION_ATTEMPTS = 100

    @staticmethod
    def generate_house_layout(user, request_data):
        valid_layout = None
        attempts = 0

        while attempts < HomeBuilderService.MAX_REGENERATION_ATTEMPTS:
            attempts += 1

            layout_data = generate_house(request_data)

            graph = build_connectivity_graph(layout_data['rooms'])

            validation_result = comprehensive_validation(
                graph=graph,
                rooms=layout_data['rooms'],
                floors=layout_data['floors'],
                length_m=layout_data['length'],
                width_m=layout_data['width']
            )

            if validation_result['is_valid']:
                valid_layout = layout_data
                break
            else:
                print(f"Layout validation failed (attempt {attempts}): {validation_result['errors']}")

        if not valid_layout:
            raise ValueError(f"Could not generate valid layout after {HomeBuilderService.MAX_REGENERATION_ATTEMPTS} attempts")

        return HomeBuilderService._save_layout_to_database(user, valid_layout, graph, request_data)

    @staticmethod
    @transaction.atomic
    def _save_layout_to_database(user, layout_data, graph, request_payload=None):
        home_layout = HomeLayout.objects.create(
            user=user,
            length=layout_data['length'],
            width=layout_data['width'],
            floors=layout_data['floors'],
            request_payload=request_payload or {}
        )

        rooms = []
        for room_data in layout_data['rooms']:
            adjacent_rooms = graph.get(room_data['id'], [])

            room = Room.objects.create(
                home=home_layout,
                room_type=room_data['type'],
                floor=room_data['floor'],
                x=room_data['x'],
                y=room_data['y'],
                width=room_data['width'],
                height=room_data['height']
            )

            room.adjacent_rooms = adjacent_rooms
            rooms.append(room)

        return home_layout

    @staticmethod
    def get_user_layouts(user):
        return HomeLayout.objects.filter(user=user).prefetch_related('rooms')

    @staticmethod
    def get_layout_with_adjacency(layout_id, user):
        try:
            home_layout = HomeLayout.objects.filter(
                id=layout_id,
                user=user
            ).prefetch_related('rooms').first()

            if not home_layout:
                return None

            rooms_data = []
            for room in home_layout.rooms.all():
                rooms_data.append({
                    'id': room.id,
                    'type': room.room_type,
                    'floor': room.floor,
                    'x': room.x,
                    'y': room.y,
                    'width': room.width,
                    'height': room.height
                })

            graph = build_connectivity_graph(rooms_data)

            for room in home_layout.rooms.all():
                room.adjacent_rooms = graph.get(room.id, [])

            return home_layout

        except HomeLayout.DoesNotExist:
            return None

    @staticmethod
    def validate_existing_layout(home_layout):
        rooms_data = []
        for room in home_layout.rooms.all():
            rooms_data.append({
                'id': room.id,
                'type': room.room_type,
                'floor': room.floor,
                'x': room.x,
                'y': room.y,
                'width': room.width,
                'height': room.height
            })

        graph = build_connectivity_graph(rooms_data)
        return comprehensive_validation(graph, rooms_data, home_layout.floors, home_layout.length, home_layout.width)