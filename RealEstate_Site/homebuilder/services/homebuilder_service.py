from django.db import transaction
from ..models import HomeLayout, Room
from .bsp import generate_house
from .room_graph import build_connectivity_graph
from .validator import comprehensive_validation


class HomeBuilderService:
    """
    Main service for generating and managing house layouts.
    Orchestrates BSP generation, graph building, and validation.
    """

    MAX_REGENERATION_ATTEMPTS = 100

    @staticmethod
    def generate_house_layout(user, request_data):
        """
        Generate a complete house layout for a user.

        Args:
            user: User instance
            request_data: Dictionary with generation parameters

        Returns:
            HomeLayout instance with rooms
        """
        # Generate layout with validation and regeneration
        valid_layout = None
        attempts = 0

        while attempts < HomeBuilderService.MAX_REGENERATION_ATTEMPTS:
            attempts += 1

            # Generate house layout using BSP
            layout_data = generate_house(request_data)

            # Build connectivity graph
            graph = build_connectivity_graph(layout_data['rooms'])

            # Validate layout
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

        # Save layout to database
        return HomeBuilderService._save_layout_to_database(user, valid_layout, graph, request_data)

    @staticmethod
    @transaction.atomic
    def _save_layout_to_database(user, layout_data, graph, request_payload=None):
        """
        Save generated layout and rooms to database.

        Args:
            user: User instance
            layout_data: Generated layout data
            graph: Connectivity graph
            request_payload: Original request payload used to generate the layout

        Returns:
            HomeLayout instance
        """
        # Create HomeLayout
        home_layout = HomeLayout.objects.create(
            user=user,
            length=layout_data['length'],
            width=layout_data['width'],
            floors=layout_data['floors'],
            request_payload=request_payload or {}
        )

        # Create Room instances
        rooms = []
        for room_data in layout_data['rooms']:
            # Get adjacent rooms from graph
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

            # Store adjacent rooms for serialization (will be used by RoomSerializer)
            room.adjacent_rooms = adjacent_rooms
            rooms.append(room)

        return home_layout

    @staticmethod
    def get_user_layouts(user):
        """
        Get all layouts for a user with their rooms.

        Args:
            user: User instance

        Returns:
            QuerySet of HomeLayout with prefetched rooms
        """
        return HomeLayout.objects.filter(user=user).prefetch_related('rooms')

    @staticmethod
    def get_layout_with_adjacency(layout_id, user):
        """
        Get a specific layout with adjacency information.

        Args:
            layout_id: HomeLayout ID
            user: User instance (for permission check)

        Returns:
            HomeLayout instance with rooms that have adjacency data
        """
        try:
            home_layout = HomeLayout.objects.filter(
                id=layout_id,
                user=user
            ).prefetch_related('rooms').first()

            if not home_layout:
                return None

            # Rebuild graph to get adjacency information
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

            # Attach adjacency data to room instances
            for room in home_layout.rooms.all():
                room.adjacent_rooms = graph.get(room.id, [])

            return home_layout

        except HomeLayout.DoesNotExist:
            return None

    @staticmethod
    def validate_existing_layout(home_layout):
        """
        Validate an existing layout from database.

        Args:
            home_layout: HomeLayout instance

        Returns:
            Validation result dictionary
        """
        # Convert rooms to dictionary format
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

        # Build graph and validate
        graph = build_connectivity_graph(rooms_data)
        return comprehensive_validation(graph, rooms_data, home_layout.floors, home_layout.length, home_layout.width)
