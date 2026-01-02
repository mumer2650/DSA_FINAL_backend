import random
from collections import defaultdict, deque
from ..models import Room


class BSPNode:
    """
    Binary Space Partitioning Node for dividing floor space.
    """
    def __init__(self, x, y, w, h, floor):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.floor = floor
        self.left = None
        self.right = None
        self.room_type = None


def normalize_units(length_m, width_m):
    """
    Normalize units from meters to internal coordinate system.

    Args:
        length_m: Length in meters
        width_m: Width in meters

    Returns:
        Dictionary with normalized dimensions and scale factors
    """
    return {
        "x": 0,
        "y": 0,
        "w": 100,  # Internal width unit
        "h": 100,  # Internal height unit
        "scale_x": length_m / 100,
        "scale_y": width_m / 100,
    }


def area_in_meters(region, scale_x, scale_y):
    """
    Calculate area of a region in square meters.

    Args:
        region: BSPNode region
        scale_x: X scale factor
        scale_y: Y scale factor

    Returns:
        Area in square meters
    """
    return (region.w * scale_x) * (region.h * scale_y)


def assign_staircase(regions, floors, current_floor):
    """
    Assign staircase in bottom-left corner for multifloored houses.
    Top floor does not get stairs.

    Args:
        regions: List of BSP regions for current floor
        floors: Total number of floors
        current_floor: Current floor number (0-based)

    Returns:
        Tuple: (stair_region, stair_position) if assigned, (None, None) otherwise
    """
    # No stairs for single floor or top floor
    if floors <= 1 or current_floor == floors - 1:
        return None, None

    # Find suitable regions for stairs
    suitable_regions = [r for r in regions if r.room_type is None]

    if not suitable_regions:
        return None, None

    # For multifloored houses, place stairs in bottom-left corner area
    # Look for regions in the bottom-left quadrant (x < 50, y > 50)
    bottom_left_regions = [
        r for r in suitable_regions
        if r.x < 50 and (r.y + r.h) > 50  # Bottom-left area
    ]

    if bottom_left_regions:
        # Choose the largest region in bottom-left
        stair_region = max(bottom_left_regions, key=lambda r: r.w * r.h)
    else:
        # Fallback: choose any suitable region
        stair_region = max(suitable_regions, key=lambda r: r.w * r.h)

    stair_region.room_type = 'STAIR'
    stair_position = (round(stair_region.x, 1), round(stair_region.y, 1))

    return stair_region, stair_position


def assign_kitchen(regions, scale_x, scale_y, kitchen_area):
    """
    Assign kitchen to a region on floor 0 with area close to requested size.

    Args:
        regions: List of BSP regions
        scale_x: X scale factor
        scale_y: Y scale factor
        kitchen_area: Requested kitchen area in square meters

    Returns:
        Kitchen region if assigned, None otherwise
    """
    # Filter regions on floor 0 that are not already assigned
    floor_0_regions = [r for r in regions if r.floor == 0 and r.room_type is None]

    # Find region with area closest to requested kitchen area (at least 80%)
    best_region = None
    best_diff = float('inf')

    for r in sorted(floor_0_regions, key=lambda r: r.w * r.h, reverse=True):
        area = area_in_meters(r, scale_x, scale_y)
        if area >= kitchen_area * 0.8:
            diff = abs(area - kitchen_area)
            if diff < best_diff:
                best_diff = diff
                best_region = r

    if best_region:
        best_region.room_type = 'KITCHEN'
        return best_region

    return None


def assign_bedroom_bath_pairs(regions, scale_x, scale_y, bath_area):
    """
    Assign bedroom and bath pairs from unassigned regions.

    Args:
        regions: List of BSP regions
        scale_x: X scale factor
        scale_y: Y scale factor
        bath_area: Requested bath area in square meters

    Returns:
        List of (bedroom, bath) pairs
    """
    unassigned = [r for r in regions if r.room_type is None]
    pairs = []

    while len(unassigned) >= 2:
        # Assign largest available as bedroom
        bedroom = max(unassigned, key=lambda r: r.w * r.h)
        unassigned.remove(bedroom)
        bedroom.room_type = 'BEDROOM'

        # Assign next largest as bath
        bath = max(unassigned, key=lambda r: r.w * r.h)
        unassigned.remove(bath)
        bath.room_type = 'BATH'

        pairs.append((bedroom, bath))

    return pairs


def assign_bedroom_bath_pairs_limited(regions, max_pairs):
    """
    Assign limited number of bedroom and bath pairs from unassigned regions.

    Args:
        regions: List of BSP regions
        max_pairs: Maximum number of pairs to create

    Returns:
        List of (bedroom, bath) pairs created
    """
    unassigned = [r for r in regions if r.room_type is None]
    pairs = []

    for _ in range(max_pairs):
        if len(unassigned) < 2:
            break

        # Assign largest available as bedroom
        bedroom = max(unassigned, key=lambda r: r.w * r.h)
        unassigned.remove(bedroom)
        bedroom.room_type = 'BEDROOM'

        # Assign next largest as bath
        bath = max(unassigned, key=lambda r: r.w * r.h)
        unassigned.remove(bath)
        bath.room_type = 'BATH'

        pairs.append((bedroom, bath))

    return pairs


def assign_hallway(regions):
    """
    Assign one region as hallway from remaining unassigned regions.
    Prefers elongated regions (length > width) which are ideal for hallways.

    Args:
        regions: List of BSP regions

    Returns:
        Hallway region if assigned, None otherwise
    """
    unassigned = [r for r in regions if r.room_type is None]
    if not unassigned:
        return None

    # Prefer elongated regions (length > width) for hallways
    elongated_regions = [r for r in unassigned if r.w > r.h]

    if elongated_regions:
        # Choose the longest elongated region
        hallway = max(elongated_regions, key=lambda r: r.w)
    else:
        # Fallback: choose the largest region by area
        hallway = max(unassigned, key=lambda r: r.w * r.h)

    hallway.room_type = 'HALL'
    return hallway


def same_floor(r1, r2):
    """
    Check if two regions are on the same floor.

    Args:
        r1, r2: BSP regions

    Returns:
        True if on same floor
    """
    return r1.floor == r2.floor


def touches(r1, r2):
    """
    Check if two regions touch each other (share an edge).

    Args:
        r1, r2: BSP regions

    Returns:
        True if regions touch
    """
    # Check horizontal adjacency
    horizontal_touch = (r1.y == r2.y + r2.h or r2.y == r1.y + r1.h) and (
        (r1.x < r2.x + r2.w and r1.x + r1.w > r2.x) or
        (r2.x < r1.x + r1.w and r2.x + r2.w > r1.x)
    )

    # Check vertical adjacency
    vertical_touch = (r1.x == r2.x + r2.w or r2.x == r1.x + r1.w) and (
        (r1.y < r2.y + r2.h and r1.y + r1.h > r2.y) or
        (r2.y < r1.y + r1.h and r2.y + r2.h > r1.y)
    )

    return horizontal_touch or vertical_touch


def build_room_graph(regions):
    """
    Build connectivity graph for rooms on the same floor.

    Args:
        regions: List of BSP regions

    Returns:
        Adjacency list graph
    """
    graph = defaultdict(list)

    for i, r1 in enumerate(regions):
        for j, r2 in enumerate(regions):
            if i != j and same_floor(r1, r2) and touches(r1, r2):
                graph[i].append(j)

    return graph


def bfs_validate(graph, regions):
    """
    Validate that all rooms are connected using BFS.

    Args:
        graph: Room connectivity graph
        regions: List of regions

    Returns:
        True if all rooms are connected
    """
    if not regions:
        return True

    visited = set()
    queue = deque([0])  # Start from first room

    while queue:
        u = queue.popleft()
        if u not in visited:
            visited.add(u)
            for v in graph[u]:
                if v not in visited:
                    queue.append(v)

    return len(visited) == len(regions)


def generate_floor_layout(floor_no, length, width, target_rooms, total_floors, min_room_size=20, max_room_size=40):
    """
    Generate room layout for a single floor using BSP tree.

    Args:
        floor_no: Floor number (0-based)
        target_rooms: Target number of rooms for this floor
        min_room_size: Minimum room size percentage
        max_room_size: Maximum room size percentage

    Returns:
        List of room dictionaries with position and size
    """
    root = BSPNode(0, 0, length, width, floor_no)
    rooms = []

    # Split the space recursively
    split_space(root, target_rooms)

    # Collect leaf nodes as rooms
    leaf_nodes = get_leaf_nodes(root)

    # Assign room types based on rules
    assign_room_types(leaf_nodes, floor_no, total_floors)

    # Convert nodes to room dictionaries
    for i, node in enumerate(leaf_nodes):
        if node.room_type:
            room = {
                'id': i + 1,
                'type': node.room_type,
                'floor': node.floor,
                'x': node.x,
                'y': node.y,
                'width': node.w,
                'height': node.h
            }
            rooms.append(room)

    return rooms


def split_space(node, target_leaves):
    """
    Simple BSP splitting to create target number of leaf regions.

    Args:
        node: Root BSP node to split
        target_leaves: Target number of leaf regions

    Returns:
        List of leaf nodes
    """
    leaves = [node]

    while len(leaves) < target_leaves:
        if not leaves:
            break

        leaf = leaves.pop(0)

        # Skip if too small to split
        if leaf.w < 20 or leaf.h < 20:
            leaves.append(leaf)
            continue

        if leaf.w > leaf.h:
            # Split vertically
            split = random.uniform(0.45, 0.55)
            left = BSPNode(leaf.x, leaf.y, leaf.w * split, leaf.h, leaf.floor)
            right = BSPNode(leaf.x + leaf.w * split, leaf.y, leaf.w * (1 - split), leaf.h, leaf.floor)
        else:
            # Split horizontally
            split = random.uniform(0.45, 0.55)
            left = BSPNode(leaf.x, leaf.y, leaf.w, leaf.h * split, leaf.floor)
            right = BSPNode(leaf.x, leaf.y + leaf.h * split, leaf.w, leaf.h * (1 - split), leaf.floor)

        leaves.extend([left, right])

    return leaves


def get_leaf_nodes(node):
    """
    Get all leaf nodes from BSP tree.

    Args:
        node: Root node of BSP tree

    Returns:
        List of leaf nodes
    """
    if node.left is None and node.right is None:
        return [node]

    leaves = []
    if node.left:
        leaves.extend(get_leaf_nodes(node.left))
    if node.right:
        leaves.extend(get_leaf_nodes(node.right))

    return leaves


def assign_room_types(nodes, floor_no, total_floors):
    """
    Assign room types to BSP leaf nodes based on rules.

    Args:
        nodes: List of leaf BSP nodes
        floor_no: Floor number
        total_floors: Total number of floors in the house
    """
    # Mandatory rooms per floor
    mandatory_rooms = []

    # Add stairway on all floors (same position across floors)
    if total_floors > 1 and floor_no == 0:
        mandatory_rooms.append('STAIR')

    # Every floor needs at least 1 bedroom and 1 hallway
    mandatory_rooms.append('BEDROOM')
    mandatory_rooms.append('HALL')

    # For multifloored houses, kitchen is mandatory only on first floor
    if floor_no == 0:
        mandatory_rooms.append('KITCHEN')

    # Assign mandatory rooms first
    assigned_count = 0
    for node in nodes:
        if assigned_count < len(mandatory_rooms):
            node.room_type = mandatory_rooms[assigned_count]
            assigned_count += 1
        else:
            break

    # Assign remaining rooms randomly from available types
    # For multifloored houses, kitchen is only on first floor, so remove from available types
    available_types = ['BEDROOM', 'BATH', 'LIVING', 'HALL']

    remaining_nodes = nodes[assigned_count:]

    for node in remaining_nodes:
        node.room_type = random.choice(available_types)

    # Apply global rules and constraints
    apply_global_rules(nodes)


def apply_global_rules(nodes):
    """
    Apply global layout rules across all floors.

    Args:
        nodes: List of BSP nodes for current floor
    """
    room_counts = defaultdict(int)
    room_positions = {}

    # Count room types and track positions
    for node in nodes:
        room_counts[node.room_type] += 1
        room_positions[node.room_type] = (node.x, node.y)

    # Rule: Only 1 kitchen per house (enforced per floor generation)
    # This will be handled at higher level

    # Rule: Ensure reasonable room distribution
    # Make sure we don't have too many of one type
    max_same_type = max(3, len(nodes) // 3)  # Allow up to 1/3 of rooms to be same type

    for room_type, count in room_counts.items():
        if count > max_same_type and room_type not in ['STAIR', 'HALL']:
            # Reduce excess rooms by converting to other types
            excess = count - max_same_type
            nodes_to_change = [n for n in nodes if n.room_type == room_type][:excess]

            for node in nodes_to_change:
                # Convert to a different type
                available_types = [t for t in ['BEDROOM', 'BATH', 'LIVING'] if t != room_type]
                node.room_type = random.choice(available_types)


def generate_house(request):
    """
    Generate house layout using rule-driven pipeline.

    Args:
        request: Dictionary with layout parameters

    Returns:
        Dictionary with generated layout
    """
    # Extract parameters
    length_m = request['length']
    width_m = request['width']
    floors = request['floors']
    rooms_per_floor = request['rooms']
    min_room_length = request['minRoomLength']
    min_room_width = request['minRoomWidth']
    kitchen_area = request['kitchenSize']
    bath_area = request['washroomSize']

    # 1. Normalize units
    normalized = normalize_units(length_m, width_m)
    scale_x = normalized['scale_x']
    scale_y = normalized['scale_y']

    all_rooms = []
    room_id_counter = 1
    # Increase attempts for multifloored houses (more complex connectivity)
    max_attempts = 20 if floors <= 2 else 50


    # Generate each floor
    for floor in range(floors):
        valid_layout = False
        attempts = 0

        while not valid_layout and attempts < max_attempts:
            # 2. Generate room regions (BSP)
            root = BSPNode(0, 0, 100, 100, floor)
            regions = split_space(root, rooms_per_floor)

            # 3. Reserve special regions in priority order
            assigned_count = 0

            # Hallway first (prefer elongated regions)
            if assign_hallway(regions):
                assigned_count += 1

            # Stairs (only for multifloored, not top floor)
            stair_region, stair_pos = assign_staircase(regions, floors, floor)
            if stair_region:
                assigned_count += 1

            # Kitchen (floor 0 only)
            if floor == 0 and assign_kitchen(regions, scale_x, scale_y, kitchen_area):
                assigned_count += 1

            # 4. Assign bedroom + bath pairs to remaining regions
            remaining_regions = rooms_per_floor - assigned_count
            if remaining_regions >= 2:  # Need at least 2 regions for a pair
                pairs_to_create = remaining_regions // 2  # Each pair needs 2 regions
                assign_bedroom_bath_pairs_limited(regions, pairs_to_create)

            # 6. Build connectivity graph
            graph = build_room_graph(regions)

            # 7. BFS validate rules
            valid_layout = bfs_validate(graph, regions)

            attempts += 1

        if not valid_layout:
            # If we couldn't generate a valid layout, assign remaining as living rooms
            for r in regions:
                if r.room_type is None:
                    r.room_type = 'LIVING'

        # Convert to room dictionaries
        for region in regions:
            if region.room_type:
                room = {
                    'id': room_id_counter,
                    'type': region.room_type,
                    'floor': region.floor,
                    'x': region.x,
                    'y': region.y,
                    'width': region.w,
                    'height': region.h
                }
                all_rooms.append(room)
                room_id_counter += 1

    return {
        'length': length_m,
        'width': width_m,
        'floors': floors,
        'rooms': all_rooms
    }


def apply_house_rules(all_rooms, floors):
    """
    Apply rules that span across the entire house.

    Args:
        all_rooms: All rooms in the house
        floors: Number of floors
    """
    # Rule: Only 1 kitchen per house
    kitchens = [r for r in all_rooms if r['type'] == 'KITCHEN']
    if len(kitchens) > 1:
        # Keep first kitchen, convert others to living rooms
        for kitchen in kitchens[1:]:
            kitchen['type'] = 'LIVING'

    # Rule: Stairways should be at same position across floors
    # stairways = [r for r in all_rooms if r['type'] == 'STAIR']
    # if stairways:
    #     # Use first stairway position as reference
    #     ref_x, ref_y = stairways[0]['x'], stairways[0]['y']
    #     for stair in stairways[1:]:
    #         stair['x'] = ref_x
    #         stair['y'] = ref_y
