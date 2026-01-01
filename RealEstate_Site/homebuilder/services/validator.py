from collections import deque


def validate_layout_with_bfs(graph, rooms, max_attempts=5):
    """
    Validate house layout using BFS algorithm.

    Args:
        graph: Room connectivity graph {room_id: [adjacent_room_ids]}
        rooms: List of room dictionaries
        max_attempts: Maximum regeneration attempts

    Returns:
        Tuple: (is_valid: bool, error_messages: list)
    """
    if not graph or not rooms:
        return False, ["No rooms or graph provided"]

    errors = []

    # Validation 1: Connectivity check - all rooms must be reachable
    connectivity_valid, connectivity_errors = validate_connectivity(graph, rooms)
    errors.extend(connectivity_errors)

    # Validation 2: Kitchen-Bath rule - kitchen should not be directly connected to bath
    kitchen_bath_valid, kitchen_bath_errors = validate_kitchen_bath_rule(graph, rooms)
    errors.extend(kitchen_bath_errors)

    # Validation 3: Bedroom-Bath rule - each bedroom must have adjacent bath
    bedroom_bath_valid, bedroom_bath_errors = validate_bedroom_bath_rule(graph, rooms)
    errors.extend(bedroom_bath_errors)

    # Overall validation result
    is_valid = connectivity_valid and kitchen_bath_valid and bedroom_bath_valid

    return is_valid, errors


def validate_connectivity(graph, rooms):
    """
    Check if all rooms are connected using BFS.

    Args:
        graph: Room connectivity graph
        rooms: List of room dictionaries

    Returns:
        Tuple: (is_valid: bool, error_messages: list)
    """
    if not rooms:
        return True, []  # Empty layout is technically valid

    # Start BFS from first room
    start_room_id = rooms[0]['id']
    visited = set()
    queue = deque([start_room_id])

    visited.add(start_room_id)

    while queue:
        current_room_id = queue.popleft()

        for adjacent_id in graph.get(current_room_id, []):
            if adjacent_id not in visited:
                visited.add(adjacent_id)
                queue.append(adjacent_id)

    # Check if all rooms were visited
    all_room_ids = {room['id'] for room in rooms}
    unvisited_rooms = all_room_ids - visited

    if unvisited_rooms:
        unvisited_room_details = []
        for room_id in unvisited_rooms:
            room = next((r for r in rooms if r['id'] == room_id), None)
            if room:
                unvisited_room_details.append(f"{room['type']} (Floor {room['floor']})")

        return False, [f"Disconnected rooms found: {', '.join(unvisited_room_details)}"]

    return True, []


def validate_kitchen_bath_rule(graph, rooms):
    """
    Validate that kitchens are not directly connected to bathrooms.

    Args:
        graph: Room connectivity graph
        rooms: List of room dictionaries

    Returns:
        Tuple: (is_valid: bool, error_messages: list)
    """
    errors = []

    # Find all kitchens
    kitchens = [room for room in rooms if room['type'] == 'KITCHEN']

    for kitchen in kitchens:
        kitchen_id = kitchen['id']
        adjacent_rooms = graph.get(kitchen_id, [])

        # Check if any adjacent room is a bathroom
        for adj_id in adjacent_rooms:
            adj_room = next((r for r in rooms if r['id'] == adj_id), None)
            if adj_room and adj_room['type'] == 'BATH':
                errors.append(f"Kitchen on floor {kitchen['floor']} is directly connected to bathroom on floor {adj_room['floor']}")
                break  # Found violation, no need to check other adjacents

    return len(errors) == 0, errors


def validate_bedroom_bath_rule(graph, rooms):
    """
    Validate that each bedroom has at least one adjacent bathroom.

    Args:
        graph: Room connectivity graph
        rooms: List of room dictionaries

    Returns:
        Tuple: (is_valid: bool, error_messages: list)
    """
    errors = []

    # Find all bedrooms
    bedrooms = [room for room in rooms if room['type'] == 'BEDROOM']

    for bedroom in bedrooms:
        bedroom_id = bedroom['id']
        adjacent_rooms = graph.get(bedroom_id, [])

        # Check if any adjacent room is a bathroom
        has_adjacent_bath = False
        for adj_id in adjacent_rooms:
            adj_room = next((r for r in rooms if r['id'] == adj_id), None)
            if adj_room and adj_room['type'] == 'BATH':
                has_adjacent_bath = True
                break

        if not has_adjacent_bath:
            errors.append(f"Bedroom on floor {bedroom['floor']} has no adjacent bathroom")

    return len(errors) == 0, errors


def get_room_by_id(rooms, room_id):
    """
    Helper function to get room by ID.

    Args:
        rooms: List of room dictionaries
        room_id: Room ID to find

    Returns:
        Room dictionary or None
    """
    for room in rooms:
        if room['id'] == room_id:
            return room
    return None


def validate_room_distribution(rooms, floors):
    """
    Validate overall room distribution rules.

    Args:
        rooms: List of room dictionaries
        floors: Number of floors

    Returns:
        Tuple: (is_valid: bool, error_messages: list)
    """
    errors = []

    # Count room types
    room_counts = {}
    for room in rooms:
        room_type = room['type']
        room_counts[room_type] = room_counts.get(room_type, 0) + 1

    # Rule: At least one bedroom per floor
    for floor in range(floors):
        floor_bedrooms = [r for r in rooms if r['floor'] == floor and r['type'] == 'BEDROOM']
        if not floor_bedrooms:
            errors.append(f"Floor {floor} has no bedrooms")

    # Rule: At least one hallway per floor
    for floor in range(floors):
        floor_halls = [r for r in rooms if r['floor'] == floor and r['type'] == 'HALL']
        if not floor_halls:
            errors.append(f"Floor {floor} has no hallways")

    # Rule: Only one kitchen per house
    kitchen_count = room_counts.get('KITCHEN', 0)
    if kitchen_count > 1:
        errors.append(f"House has {kitchen_count} kitchens, but only 1 is allowed")

    # Rule: At least one stairway per floor
    for floor in range(floors):
        floor_stairs = [r for r in rooms if r['floor'] == floor and r['type'] == 'STAIR']
        if not floor_stairs:
            errors.append(f"Floor {floor} has no stairway")

    return len(errors) == 0, errors


def comprehensive_validation(graph, rooms, floors, max_regeneration_attempts=3):
    """
    Perform comprehensive validation of house layout.

    Args:
        graph: Room connectivity graph
        rooms: List of room dictionaries
        floors: Number of floors
        max_regeneration_attempts: Maximum attempts to regenerate invalid layouts

    Returns:
        Dictionary with validation results
    """
    # Perform all validations
    bfs_valid, bfs_errors = validate_layout_with_bfs(graph, rooms)
    dist_valid, dist_errors = validate_room_distribution(rooms, floors)

    all_errors = bfs_errors + dist_errors
    is_valid = bfs_valid and dist_valid

    return {
        'is_valid': is_valid,
        'errors': all_errors,
        'connectivity_valid': bfs_valid,
        'distribution_valid': dist_valid,
        'needs_regeneration': not is_valid
    }
