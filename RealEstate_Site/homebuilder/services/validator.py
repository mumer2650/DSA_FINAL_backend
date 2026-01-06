from collections import deque

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
            queue = deque([room_id])

            while queue:
                current_id = queue.popleft()
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
            queue = deque([room_id])

            while queue:
                current_id = queue.popleft()
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
        if not floor_bedrooms and not floor == 0:
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
    
