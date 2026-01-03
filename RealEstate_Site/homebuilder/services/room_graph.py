from collections import defaultdict


def build_connectivity_graph(rooms):
    """
    Build a connectivity graph where rooms are nodes and edges represent adjacency.

    Args:
        rooms: List of room dictionaries

    Returns:
        Dictionary representing adjacency list: {room_id: [adjacent_room_ids]}
    """
    graph = defaultdict(list)

    # Group rooms by floor for easier adjacency checking
    rooms_by_floor = defaultdict(list)
    for room in rooms:
        rooms_by_floor[room['floor']].append(room)

    # Check adjacency for rooms on the same floor
    for floor_rooms in rooms_by_floor.values():
        for i, room1 in enumerate(floor_rooms):
            for j, room2 in enumerate(floor_rooms):
                if i != j and are_adjacent(room1, room2):
                    graph[room1['id']].append(room2['id'])

    # Add vertical connections for stairways
    add_stairway_connections(graph, rooms)

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
