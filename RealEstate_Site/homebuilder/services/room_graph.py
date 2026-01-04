from collections import defaultdict


# def are_adjacent(room1, room2):
#     """
#     Check if two rooms are adjacent (share a wall).

#     Args:
#         room1, room2: Room dictionaries

#     Returns:
#         True if rooms share a wall
#     """
#     # Must be on the same floor
#     if room1['floor'] != room2['floor']:
#         return False

#     # Calculate boundaries
#     r1_left = room1['x']
#     r1_right = room1['x'] + room1['width']
#     r1_top = room1['y']
#     r1_bottom = room1['y'] + room1['height']

#     r2_left = room2['x']
#     r2_right = room2['x'] + room2['width']
#     r2_top = room2['y']
#     r2_bottom = room2['y'] + room2['height']

#     # Tolerance for floating point precision
#     tolerance = 0.1

#     # Horizontal adjacency (same y-level)
#     horizontal_adj = (
#         abs(r1_bottom - r2_top) < tolerance or abs(r2_bottom - r1_top) < tolerance
#     ) and (
#         (r1_left < r2_right - tolerance and r1_right > r2_left + tolerance) or
#         (r2_left < r1_right - tolerance and r2_right > r1_left + tolerance)
#     )

#     # Vertical adjacency (same x-level)
#     vertical_adj = (
#         abs(r1_right - r2_left) < tolerance or abs(r2_right - r1_left) < tolerance
#     ) and (
#         (r1_top < r2_bottom - tolerance and r1_bottom > r2_top + tolerance) or
#         (r2_top < r1_bottom - tolerance and r2_bottom > r1_top + tolerance)
#     )

#     return horizontal_adj or vertical_adj


def build_connectivity_graph(rooms):
    """
    Build a connectivity graph with updated architectural connection rules.

    Connection Rules (ONLY THESE):
    - KDL_HUB <-> adjacent rooms (HALL, STAIR, BSP rooms)
    - HALL <-> adjacent rooms (KDL, STAIR, BSP rooms)
    - STAIR <-> STAIR (vertical only, same x/y)
    -  Do NOT connect: BSP ↔ BSP directly, Bedroom ↔ Bedroom implicitly,
      Rooms across hallway unless they share a boundary
    - Adjacency = shared edge, not proximity

    Args:
        rooms: List of room dictionaries

    Returns:
        Dictionary representing adjacency list: {room_id: [adjacent_room_ids]}
    """
    graph = defaultdict(list)

    # Group rooms by floor and type for easier processing
    rooms_by_floor = defaultdict(list)
    stairways = []
    hallways = []
    kdl_hubs = []

    for room in rooms:
        rooms_by_floor[room['floor']].append(room)
        if room['type'] == 'STAIR':
            stairways.append(room)
        elif room['type'] == 'HALL':
            hallways.append(room)
        elif room['type'] == 'KITCHEN_LIVING_DINING_HUB':
            kdl_hubs.append(room)

    # Rule 1: KDL_HUB <-> adjacent rooms (HALL, STAIR, BSP rooms)
    for kdl_hub in kdl_hubs:
        floor_rooms = rooms_by_floor[kdl_hub['floor']]
        # KDL connects to HALL, STAIR, and BSP rooms (LIVING, ATTACHED_BED_BATH, STUDYROOM, STORAGE)
        connectable_types = ['HALL', 'STAIR', 'LIVING', 'ATTACHED_BED_BATH', 'STUDYROOM', 'STORAGE']

        for room in floor_rooms:
            if room['type'] in connectable_types and room['id'] != kdl_hub['id']:
                if are_adjacent(kdl_hub, room):
                    graph[kdl_hub['id']].append(room['id'])
                    graph[room['id']].append(kdl_hub['id'])

    # Rule 2: HALL <-> adjacent rooms (KDL, STAIR, BSP rooms)
    for hall in hallways:
        floor_rooms = rooms_by_floor[hall['floor']]
        # HALL connects to KDL_HUB, STAIR, and BSP rooms
        connectable_types = ['KITCHEN_LIVING_DINING_HUB', 'STAIR', 'LIVING', 'ATTACHED_BED_BATH', 'STUDYROOM', 'STORAGE']

        for room in floor_rooms:
            if room['type'] in connectable_types and room['id'] != hall['id']:
                if are_adjacent(hall, room):
                    graph[hall['id']].append(room['id'])
                    graph[room['id']].append(hall['id'])

    # Rule 3: STAIR <-> STAIR (vertical only, same x/y)
    # This is handled by add_stairway_connections function

    # Rule 4: STAIR <-> HALL (if adjacent on same floor)
    for stair in stairways:
        for hall in hallways:
            if stair['floor'] == hall['floor'] and are_adjacent(stair, hall):
                graph[stair['id']].append(hall['id'])
                graph[hall['id']].append(stair['id'])

    # Add vertical stair connections
    add_stairway_connections(graph, rooms)

    # IMPORTANT: Do NOT add any BSP ↔ BSP connections or implicit bedroom connections
    # Only the explicit rules above should create connections

    return dict(graph)


def are_adjacent(room1, room2):
    """
    Check if two rooms are adjacent (share a wall).

    Args:
        room1: First room dictionary
        room2: Second room dictionary

    Returns:
        Boolean indicating if rooms are adjacent
    """
    # Must be on the same floor
    if room1['floor'] != room2['floor']:
        return False

    # Calculate room boundaries
    r1_left = room1['x']
    r1_right = room1['x'] + room1['width']
    r1_top = room1['y']
    r1_bottom = room1['y'] + room1['height']

    r2_left = room2['x']
    r2_right = room2['x'] + room2['width']
    r2_top = room2['y']
    r2_bottom = room2['y'] + room2['height']

    # Check for adjacency with small tolerance for floating point precision
    tolerance = 0.1

    # Check if they share a vertical edge (left or right sides touch)
    vertical_adjacent = (
        abs(r1_right - r2_left) < tolerance or
        abs(r2_right - r1_left) < tolerance
    ) and (
        # Check if they overlap vertically
        (r1_top < r2_bottom - tolerance and r1_bottom > r2_top + tolerance) or
        (r2_top < r1_bottom - tolerance and r2_bottom > r1_top + tolerance)
    )

    # Check if they share a horizontal edge (top or bottom sides touch)
    horizontal_adjacent = (
        abs(r1_bottom - r2_top) < tolerance or
        abs(r2_bottom - r1_top) < tolerance
    ) and (
        # Check if they overlap horizontally
        (r1_left < r2_right - tolerance and r1_right > r2_left + tolerance) or
        (r2_left < r1_right - tolerance and r2_right > r1_left + tolerance)
    )

    return vertical_adjacent or horizontal_adjacent


def add_stairway_connections(graph, rooms):
    """
    Add vertical connections between stairways on different floors.

    Args:
        graph: Adjacency graph to modify
        rooms: List of all rooms
    """
    # Find all stairways
    stairways = [room for room in rooms if room['type'] == 'STAIR']

    # Group stairways by their (x, y) position
    stairway_groups = defaultdict(list)

    for stair in stairways:
        # Round coordinates to handle floating point precision
        key = (round(stair['x'], 1), round(stair['y'], 1))
        stairway_groups[key].append(stair)

    # Connect stairways at the same position across floors
    for position, stairs_at_pos in stairway_groups.items():
        if len(stairs_at_pos) > 1:
            # Sort by floor
            stairs_at_pos.sort(key=lambda s: s['floor'])

            # Connect consecutive floors
            for i in range(len(stairs_at_pos) - 1):
                current_stair = stairs_at_pos[i]
                next_stair = stairs_at_pos[i + 1]

                # Add bidirectional connection
                graph[current_stair['id']].append(next_stair['id'])
                graph[next_stair['id']].append(current_stair['id'])


def get_room_by_id(rooms, room_id):
    """
    Get room dictionary by ID.

    Args:
        rooms: List of room dictionaries
        room_id: Room ID to find

    Returns:
        Room dictionary or None if not found
    """
    for room in rooms:
        if room['id'] == room_id:
            return room
    return None


def print_graph(graph, rooms):
    """
    Debug function to print the connectivity graph.

    Args:
        graph: Adjacency graph
        rooms: List of room dictionaries
    """
    print("Room Connectivity Graph:")
    for room_id, adjacents in graph.items():
        room = get_room_by_id(rooms, room_id)
        if room:
            adj_rooms = []
            for adj_id in adjacents:
                adj_room = get_room_by_id(rooms, adj_id)
                if adj_room:
                    adj_rooms.append(f"{adj_room['type']}(F{adj_room['floor']})")

            print(f"Room {room_id} ({room['type']} F{room['floor']}): {adj_rooms}")
