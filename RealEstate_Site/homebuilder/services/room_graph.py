from collections import defaultdict

def build_connectivity_graph(rooms):
    """
    Build adjacency graph for rooms.
    Returns: dict {room_id: [adjacent_room_ids]}
    """
    graph = defaultdict(list)

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

    for kdl_hub in kdl_hubs:
        floor_rooms = rooms_by_floor[kdl_hub['floor']]
        connectable_types = ['HALL', 'STAIR', 'LIVING', 'ATTACHED_BED_BATH', 'STUDYROOM', 'STORAGE']

        for room in floor_rooms:
            if room['type'] in connectable_types and room['id'] != kdl_hub['id']:
                if are_adjacent(kdl_hub, room):
                    graph[kdl_hub['id']].append(room['id'])
                    graph[room['id']].append(kdl_hub['id'])

    for hall in hallways:
        floor_rooms = rooms_by_floor[hall['floor']]
        connectable_types = ['KDL_HUB', 'STAIR', 'LIVING', 'ATTACHED_BED_BATH', 'STUDYROOM', 'STORAGE']

        for room in floor_rooms:
            if room['type'] in connectable_types and room['id'] != hall['id']:
                if are_adjacent(hall, room):
                    graph[hall['id']].append(room['id'])
                    graph[room['id']].append(hall['id'])

    for stair in stairways:
        if stair['type'] == 'STAIR':
            for other_stair in stairways:
                if other_stair != stair and are_adjacent_stairs(stair, other_stair):
                    graph[stair['id']].append(other_stair['id'])

    return graph

def are_adjacent(room1, room2):
    if room1['floor'] != room2['floor']:
        return False

    r1_left = room1['x']
    r1_right = room1['x'] + room1['width']
    r1_top = room1['y']
    r1_bottom = room1['y'] + room1['height']

    r2_left = room2['x']
    r2_right = room2['x'] + room2['width']
    r2_top = room2['y']
    r2_bottom = room2['y'] + room2['height']

    tolerance = 0.1

    horizontal_adj = (
        abs(r1_bottom - r2_top) < tolerance or abs(r2_bottom - r1_top) < tolerance
    ) and (
        (r1_left < r2_right - tolerance and r1_right > r2_left + tolerance) or
        (r2_left < r1_right - tolerance and r2_right > r1_left + tolerance)
    )

    vertical_adj = (
        abs(r1_right - r2_left) < tolerance or abs(r2_right - r1_left) < tolerance
    ) and (
        (r1_top < r2_bottom - tolerance and r1_bottom > r2_top + tolerance) or
        (r2_top < r1_bottom - tolerance and r2_bottom > r1_top + tolerance)
    )

    return horizontal_adj or vertical_adj

def are_adjacent_stairs(stair1, stair2):
    if stair1['floor'] == stair2['floor']:
        return False

    tolerance = 5.0

    center1_x = stair1['x'] + stair1['width'] / 2
    center1_y = stair1['y'] + stair1['height'] / 2
    center2_x = stair2['x'] + stair2['width'] / 2
    center2_y = stair2['y'] + stair2['height'] / 2

    return abs(center1_x - center2_x) < tolerance and abs(center1_y - center2_y) < tolerance

def validate_layout_with_bfs(graph, rooms, max_attempts=5):
    if not graph or not rooms:
        return False, ["No rooms or graph provided"]

    errors = []

    all_room_ids = {room['id'] for room in rooms}
    visited = set()
    components = []

    for room_id in all_room_ids:
        if room_id not in visited:
            component = set()
            queue = [room_id]

            while queue:
                current_id = queue.pop(0)
                if current_id not in component:
                    component.add(current_id)
                    visited.add(current_id)
                    queue.extend(graph.get(current_id, []))

            components.append(component)

    if len(components) > 4:
        component_details = []
        for i, component in enumerate(components):
            room_details = []
            for room_id in component:
                room = next((r for r in rooms if r['id'] == room_id), None)
                if room:
                    room_details.append(f"{room['type']}(F{room['floor']})")
            component_details.append(f"Component {i+1}: {', '.join(room_details)}")

        return False, [f"Too many disconnections: {len(components)} separate components. " +
                      f"Components: {'; '.join(component_details)}"]

    return True, []

def validate_connectivity(graph, rooms):
    if not rooms:
        return True, []

    all_room_ids = {room['id'] for room in rooms}
    visited = set()
    components = []

    for room_id in all_room_ids:
        if room_id not in visited:
            component = set()
            queue = [room_id]

            while queue:
                current_id = queue.pop(0)
                if current_id not in component:
                    component.add(current_id)
                    visited.add(current_id)
                    queue.extend(graph.get(current_id, []))

            components.append(component)

    if len(components) > 4:
        component_details = []
        for i, component in enumerate(components):
            room_details = []
            for room_id in component:
                room = next((r for r in rooms if r['id'] == room_id), None)
                if room:
                    room_details.append(f"{room['type']}(F{room['floor']})")
            component_details.append(f"Component {i+1}: {', '.join(room_details)}")

        return False, [f"Too many disconnections: {len(components)} separate components. " +
                      f"Components: {'; '.join(component_details)}"]

    return True, []

def validate_kitchen_bath_rule(graph, rooms):
    errors = []

    kitchens = [room for room in rooms if room['type'] == 'KITCHEN']

    for kitchen in kitchens:
        kitchen_id = kitchen['id']
        adjacent_rooms = graph.get(kitchen_id, [])

        for adj_id in adjacent_rooms:
            adj_room = next((r for r in rooms if r['id'] == adj_id), None)
            if adj_room and adj_room['type'] == 'BATH':
                errors.append(f"Kitchen on floor {kitchen['floor']} is directly connected to bathroom on floor {adj_room['floor']}")
                break

    return len(errors) == 0, errors

def validate_bedroom_bath_rule(graph, rooms):
    errors = []

    bedrooms = [room for room in rooms if room['type'] == 'BEDROOM']

    for bedroom in bedrooms:
        bedroom_id = bedroom['id']
        adjacent_rooms = graph.get(bedroom_id, [])

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
    for room in rooms:
        if room['id'] == room_id:
            return room
    return None

def validate_room_distribution(rooms, floors, layout_case=None, length_m=None, width_m=None):
    errors = []

    room_counts = {}
    for room in rooms:
        room_type = room['type']
        room_counts[room_type] = room_counts.get(room_type, 0) + 1

    for floor in range(floors):
        floor_bedrooms = [r for r in rooms if r['floor'] == floor and r['type'] == 'ATTACHED_BED_BATH']
        if not floor_bedrooms:
            errors.append(f"Floor {floor} has no attached bedrooms")

    for floor in range(floors):
        floor_halls = [r for r in rooms if r['floor'] == floor and r['type'] == 'HALL']

        skip_hallway_check = False

        if layout_case == "SINGLE_SIDED_HALL" and floors > 1 and floor == 0:
            skip_hallway_check = True
        elif layout_case == "COMPACT" and floor == 0:
            skip_hallway_check = True

        if not skip_hallway_check and not floor_halls:
            errors.append(f"Floor {floor} has no hallways")

    kdl_count = room_counts.get('KITCHEN_LIVING_DINING_HUB', 0)
    if kdl_count > 1:
        errors.append(f"House has {kdl_count} KDL hubs, but only 1 is allowed")

    if floors > 1:
        for floor in range(floors-1):
            floor_stairs = [r for r in rooms if r['floor'] == floor and r['type'] == 'STAIR']
            if not floor_stairs:
                errors.append(f"Floor {floor} has no stairway")

    return len(errors) == 0, errors

def comprehensive_validation(graph, rooms, floors, length_m=None, width_m=None, max_regeneration_attempts=3):
    if length_m is not None and width_m is not None:
        layout_case = detect_layout_case(length_m, width_m)
    else:
        layout_case = None

    bfs_valid, bfs_errors = validate_layout_with_bfs(graph, rooms)
    dist_valid, dist_errors = validate_room_distribution(rooms, floors, layout_case, length_m, width_m)

    all_errors = bfs_errors + dist_errors
    is_valid = bfs_valid and dist_valid

    return {
        'is_valid': is_valid,
        'errors': all_errors,
        'connectivity_valid': bfs_valid,
        'distribution_valid': dist_valid,
        'needs_regeneration': not is_valid
    }

def detect_layout_case(length_m, width_m):
    if width_m > 70:
        return "DOUBLE_SIDED_HALL"
    elif width_m > 50:
        return "SINGLE_SIDED_HALL"
    else:
        return "COMPACT"