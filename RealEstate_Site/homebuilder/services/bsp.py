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


def detect_layout_case(length_m, width_m):
    """
    Detect which layout case to use based on house dimensions.

    Args:
        length_m: House length in meters
        width_m: House width in meters

    Returns:
        Layout case string: "DOUBLE_SIDED_HALL", "SINGLE_SIDED_HALL", or "COMPACT"
    """
    # Layout cases based on width ranges
    if width_m > 70:  # 70-100 meters
        return "DOUBLE_SIDED_HALL"
    elif width_m > 50:  # 50-70 meters
        return "SINGLE_SIDED_HALL"
    else:  # 40-50 meters
        return "COMPACT"


def create_structural_elements(length_m, width_m, floors, current_floor):
    """
    Create deterministic structural elements based on layout case and floor type.

    Args:
        length_m: House length in meters
        width_m: House width in meters
        floors: Total number of floors
        current_floor: Current floor number (0-based)

    Returns:
        Tuple: (structural_regions, bsp_zones)
        structural_regions: List of BSPNode objects for structural elements
        bsp_zones: List of BSPNode objects defining areas for BSP room generation
    """
    layout_case = detect_layout_case(length_m, width_m)
    structural_regions = []
    bsp_zones = []
    is_ground_floor = (current_floor == 0)
    is_multi_floor = (floors > 1)

    if layout_case == "DOUBLE_SIDED_HALL":
        # Double-sided hallway layout (width: 70-100m)
        hallway_width_percent = 10  # 10% of house width
        hallway_width = hallway_width_percent  # in internal units

        if is_ground_floor:
            # Ground floor: KDL Hub + Hall + BSP on both sides
            kdl_height_percent = 60  # 60% for KDL Hub
            bsp_height_percent = 40  # 40% for BSP regions

            # KDL Hub on left side (top)
            kdl_hub = BSPNode(
                x=0,
                y=0,
                w=45,  # 45% width for KDL Hub
                h=kdl_height_percent,
                floor=current_floor
            )
            kdl_hub.room_type = "KITCHEN_LIVING_DINING_HUB"
            structural_regions.append(kdl_hub)

            # Central hallway
            hallway = BSPNode(
                x=kdl_hub.w,  # Right of KDL Hub
                y=0,
                w=hallway_width,
                h=100,  # Full height
                floor=current_floor
            )
            hallway.room_type = "HALL"
            structural_regions.append(hallway)

            # Stairs at bottom of hallway if multi-floor
            if is_multi_floor:
                stair_height_percent = 20  # 20% of house length
                stairs = BSPNode(
                    x=hallway.x,
                    y=hallway.h - stair_height_percent,
                    w=hallway.w,
                    h=stair_height_percent,
                    floor=current_floor
                )
                stairs.room_type = "STAIR"
                structural_regions.append(stairs)
                hallway.h = hallway.h - stair_height_percent

            # BSP zones on both sides
            left_bsp = BSPNode(
                x=0,
                y=kdl_height_percent,  # Below KDL Hub
                w=45,  # Same width as KDL Hub
                h=bsp_height_percent,
                floor=current_floor
            )
            bsp_zones.append(left_bsp)

            right_bsp = BSPNode(
                x=hallway.x + hallway.w,  # Right of hallway
                y=0,
                w=45,  # Remaining width
                h=100,
                floor=current_floor
            )
            bsp_zones.append(right_bsp)

        else:
            # Upper floors: BSP + Hall + BSP
            # Central hallway
            stair_height_percent = 20
            hallway = BSPNode(
                x=(100 - hallway_width) / 2,  # Centered
                y=0,
                w=hallway_width,
                h=100-stair_height_percent,
                floor=current_floor
            )
            hallway.room_type = "HALL"
            structural_regions.append(hallway)

            # Stairs aligned with lower floors
            if is_multi_floor:
                stair_height_percent = 20
                stairs = BSPNode(
                    x=hallway.x,
                    y=hallway.h,
                    w=hallway.w,
                    h=stair_height_percent,
                    floor=current_floor
                )
                stairs.room_type = "STAIR"
                structural_regions.append(stairs)
                # hallway.h = hallway.h - stair_height_percent

            # BSP zones on both sides
            left_bsp = BSPNode(
                x=0,
                y=0,
                w=hallway.x,
                h=100,
                floor=current_floor
            )
            bsp_zones.append(left_bsp)

            right_bsp = BSPNode(
                x=hallway.x + hallway.w,
                y=0,
                w=100 - (hallway.x + hallway.w),
                h=100,
                floor=current_floor
            )
            bsp_zones.append(right_bsp)

    elif layout_case == "SINGLE_SIDED_HALL":
        # Single-sided hallway layout (width: 50-70m)
        hallway_width_percent = 20  # 20% width
        bsp_height_percent = 60  # 60% for BSP
        

        if is_ground_floor:
            # Ground floor: Hall + KDL Hub + BSP below
            kdl_height_percent = 40  # 40% for KDL Hub

            # Left hallway
            hallway = BSPNode(
                x=0,
                y=0,
                w=hallway_width_percent,
                h=40,
                floor=current_floor
            )
            hallway.room_type = "HALL"
            structural_regions.append(hallway)

            # KDL Hub to the right of hallway
            kdl_hub = BSPNode(
                x=hallway_width_percent,
                y=0,
                w=80,  # 80% remaining width
                h=kdl_height_percent,
                floor=current_floor
            )
            kdl_hub.room_type = "KITCHEN_LIVING_DINING_HUB"
            structural_regions.append(kdl_hub)

            # Stairs at bottom of hallway if multi-floor
            if is_multi_floor:
                structural_regions.remove(hallway)
                stairs = BSPNode(
                    x=0,
                    y=0,
                    w=hallway_width_percent,
                    h=40,
                    floor=current_floor
                )
                stairs.room_type = "STAIR"
                structural_regions.append(stairs)

            # BSP zone below KDL Hub
            bsp_zone = BSPNode(
                x=0,
                y=kdl_height_percent,
                w=100,
                h=bsp_height_percent,
                floor=current_floor
            )
            bsp_zones.append(bsp_zone)

        else:
            # hallway_width_percent = 80
            hallway_height_percent = 40  # 40% for hallway height
            # hallway_height_percent = 40
            # Upper floors: Hall + BSP
            hallway = BSPNode(
            x=hallway_width_percent,
            y=0,
            w=80,  # 80% remaining width
            h=hallway_height_percent,
            floor=current_floor
            )
            hallway.room_type = "HALL"
            structural_regions.append(hallway)

            # Stairs aligned with ground floor
            if is_multi_floor:
                # Left hallway
                stairs = BSPNode(
                x=0,
                y=0,
                w=hallway_width_percent,
                h=40,
                floor=current_floor
                )
                stairs.room_type = "STAIR"
                structural_regions.append(stairs)


            # BSP zone to the right
            bsp_zone = BSPNode(
                x=0,
                y=hallway_height_percent,
                w=100,
                h=bsp_height_percent,
                floor=current_floor
            )
            bsp_zones.append(bsp_zone)

    else:  # COMPACT (width: 40-50m)
        if is_ground_floor:
            # Ground floor: Simple vertical split
            kdl_height_percent = 40  # 40% for KDL Hub
            bsp_height_percent = 60  # 60% for BSP

            # KDL Hub at top
            kdl_hub = BSPNode(
                x=0,
                y=0,
                w=100,  # Full width
                h=kdl_height_percent,
                floor=current_floor
            )
            kdl_hub.room_type = "KITCHEN_LIVING_DINING_HUB"
            structural_regions.append(kdl_hub)

            # Stairs at top-left if multi-floor
            if is_multi_floor:
                stair_width_percent = 20  # 20% width and height
                stair_height_percent = 40  # 20% width and height
                stairs = BSPNode(
                    x=0,
                    y=0,
                    w=stair_width_percent,
                    h=stair_height_percent,
                    floor=current_floor
                )
                stairs.room_type = "STAIR"
                structural_regions.append(stairs)

                # Adjust KDL Hub to account for stairs
                kdl_hub.x = stair_width_percent
                kdl_hub.w = 100 - stair_width_percent

            # BSP zone below
            bsp_zone = BSPNode(
                x=0,
                y=kdl_height_percent,
                w=100,
                h=bsp_height_percent,
                floor=current_floor
            )
            bsp_zones.append(bsp_zone)

        else:
            # Upper floors: Stair + Hall + BSP
            stair_hall_width_percent = 20
            upper_bsp_width_percent = 60
            stair_hall_height_percent = 40

            # Stairs at top-left
            stairs = BSPNode(
                x=0,
                y=0,
                w=stair_hall_width_percent,
                h=stair_hall_height_percent,
                floor=current_floor
            )
            stairs.room_type = "STAIR"
            structural_regions.append(stairs)

            # Hallway next to stairs
            hallway = BSPNode(
                x=stair_hall_width_percent,
                y=0,
                w=stair_hall_width_percent,
                h=stair_hall_height_percent,  # Same height as stairs for connectivity
                floor=current_floor
            )
            hallway.room_type = "HALL"
            structural_regions.append(hallway)

            # BSP zone to the right
            upper_bsp_zone = BSPNode(
                x=stair_hall_width_percent + stair_hall_width_percent,
                y=0,
                w=upper_bsp_width_percent,
                h=stair_hall_height_percent,
                floor=current_floor
            )
            bsp_zones.append(upper_bsp_zone)

            # Additional BSP zone below hallway area
            bottom_bsp = BSPNode(
                x=0,
                y=stair_hall_height_percent,
                w=100,
                h=100 - stair_hall_height_percent,
                floor=current_floor
            )
            bsp_zones.append(bottom_bsp)

    return structural_regions, bsp_zones


def distribute_bedrooms_across_floors(total_bedrooms, floors):
    """
    Distribute totalBedrooms evenly across floors.

    Args:
        total_bedrooms: Total number of ATTACHED_BED_BATH units
        floors: Total number of floors

    Returns:
        List where index is floor number and value is bedrooms for that floor
    """
    bedrooms_per_floor = [total_bedrooms // floors] * floors
    remainder = total_bedrooms % floors

    # Distribute remainder starting from ground floor
    for i in range(remainder):
        bedrooms_per_floor[i] += 1

    return bedrooms_per_floor


def get_floor_room_requirements(total_rooms, bedrooms_per_floor, floors, current_floor):
    """
    Determine what room types are needed for this floor.

    Args:
        total_rooms: Total rooms in entire house
        bedrooms_per_floor: List of bedrooms per floor
        floors: Total floors
        current_floor: Current floor number (0-based)

    Returns:
        Dict with room type requirements for this floor
    """
    requirements = {
        'ATTACHED_BED_BATH': bedrooms_per_floor[current_floor],
        'STUDYROOM': 0,
        'STORAGE': 0,
        'LIVING': 0
    }

    # Special room assignments based on floor
    if floors >= 3:
        # Last floor gets STORAGE
        if current_floor == floors - 1:
            requirements['STORAGE'] = 1
        # Second floor gets STUDYROOM
        elif current_floor == 1:
            requirements['STUDYROOM'] = 1
    elif floors == 2:
        # Second floor gets both STUDYROOM and STORAGE if space allows
        if current_floor == 1:
            requirements['STUDYROOM'] = 1
            requirements['STORAGE'] = 1

    # Calculate remaining slots for LIVING rooms
    used_slots = (requirements['ATTACHED_BED_BATH'] +
                 requirements['STUDYROOM'] +
                 requirements['STORAGE'])

    # Ground floor doesn't get LIVING rooms
    if current_floor == 0:
        requirements['LIVING'] = 0
    else:
        # Distribute remaining rooms as LIVING, but respect total house rooms
        remaining_house_rooms = total_rooms - sum(bedrooms_per_floor)
        if floors > 1:
            living_per_upper_floor = remaining_house_rooms // (floors - 1)
            requirements['LIVING'] = max(0, living_per_upper_floor - used_slots + requirements['ATTACHED_BED_BATH'] + requirements['STUDYROOM'] + requirements['STORAGE'])

    return requirements


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


def assign_room_types_to_zone(zone_regions, floor, total_floors, zone_idx, floor_requirements,
                             bedrooms_assigned, scale_x, scale_y):
    """
    Assign room types to regions within a single zone following the new assignment order.

    Args:
        zone_regions: List of BSPNode regions in this zone
        floor: Current floor number
        total_floors: Total floors in house
        zone_idx: Index of this zone on the floor
        floor_requirements: Dict with room type requirements for this floor
        bedrooms_assigned: Number of bedrooms already assigned to this floor
        scale_x, scale_y: Scale factors

    Returns:
        Tuple: (regions with assigned types, bedrooms_assigned_to_zone)
    """
    # Sort regions by area (largest first) for assignment
    unassigned = sorted([r for r in zone_regions if r.room_type is None],
                       key=lambda r: r.w * r.h, reverse=True)

    bedrooms_assigned_to_zone = 0

    # 1. Assign ATTACHED_BED_BATH until floor quota reached
    bedrooms_needed = floor_requirements['ATTACHED_BED_BATH'] - bedrooms_assigned
    bedrooms_to_assign = min(bedrooms_needed, len(unassigned))

    for i in range(bedrooms_to_assign):
        if unassigned:
            region = unassigned.pop(0)
            region.room_type = 'ATTACHED_BED_BATH'
            bedrooms_assigned_to_zone += 1

    # 2. Assign STUDYROOM if needed and this is the appropriate floor
    if floor_requirements['STUDYROOM'] > 0 and unassigned:
        region = unassigned.pop(0)
        region.room_type = 'STUDYROOM'

    # 3. Assign STORAGE if needed and this is the appropriate floor
    if floor_requirements['STORAGE'] > 0 and unassigned:
        region = unassigned.pop(0)
        region.room_type = 'STORAGE'

    # 4. Assign remaining rooms as LIVING (not on ground floor)
    for region in unassigned:
        if floor > 0:  # Not ground floor
            region.room_type = 'LIVING'
        else:
            # Ground floor gets no LIVING rooms, leave unassigned or assign as needed
            region.room_type = 'LIVING'  # Allow on ground floor if space

    return zone_regions, bedrooms_assigned_to_zone


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





def split_space(node, target_leaves, min_room_length_m, min_room_width_m, scale_x, scale_y):
    """
    Simple BSP splitting to create target number of leaf regions within a zone.

    Args:
        node: Root BSP node to split (represents a zone)
        target_leaves: Target number of leaf regions
        min_room_length_m: Minimum room length in meters
        min_room_width_m: Minimum room width in meters
        scale_x: X scale factor (meters per internal unit)
        scale_y: Y scale factor (meters per internal unit)

    Returns:
        List of leaf nodes
    """
    print(f"split_space called: zone size {node.w}x{node.h}, target_leaves={target_leaves}")

    # Convert minimum dimensions from meters to internal units
    min_room_width_internal = min_room_width_m / scale_x
    min_room_length_internal = min_room_length_m / scale_y

    leaves = [node]

    # Adjust target based on zone size - don't try to create too many rooms in small zones
    # Use the actual minimum room area for the heuristic
    min_room_area = min_room_width_internal * min_room_length_internal
    max_possible = min(target_leaves, max(1, int((node.w * node.h) / (min_room_area * 2))))
    actual_target = min(target_leaves, max_possible)

    # Prevent infinite loops - limit iterations
    max_iterations = 100
    iterations = 0

    while len(leaves) < actual_target and iterations < max_iterations:
        iterations += 1
        if not leaves:
            break

        leaf = leaves.pop(0)

        # Skip if too small to split (using actual minimum room dimensions)
        if leaf.w < min_room_width_internal * 1.8 or leaf.h < min_room_length_internal * 1.8:
            leaves.append(leaf)
            continue

        if leaf.w > leaf.h:
            # Split vertically (along width)
            split = random.uniform(0.4, 0.6)  # Slightly more centered split
            left = BSPNode(leaf.x, leaf.y, leaf.w * split, leaf.h, leaf.floor)
            right = BSPNode(leaf.x + leaf.w * split, leaf.y, leaf.w * (1 - split), leaf.h, leaf.floor)
        else:
            # Split horizontally (along height)
            split = random.uniform(0.4, 0.6)
            left = BSPNode(leaf.x, leaf.y, leaf.w, leaf.h * split, leaf.floor)
            right = BSPNode(leaf.x, leaf.y + leaf.h * split, leaf.w, leaf.h * (1 - split), leaf.floor)

        leaves.extend([left, right])

    # If we couldn't reach the target due to space constraints, use what we have
    print(f"split_space returning {len(leaves)} leaves (target was {actual_target}, iterations: {iterations})")
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


def generate_house(request):
    """
    Generate house layout using rule-driven pipeline with new room types and logic.

    Args:
        request: Dictionary with layout parameters

    Returns:
        Dictionary with generated layout
    """
    # Extract parameters
    length_m = request['length']
    width_m = request['width']
    floors = request['floors']
    total_rooms = request['rooms']  # Total rooms in entire house
    min_room_length = request['minRoomLength']
    min_room_width = request['minRoomWidth']
    kitchen_area = request['kitchenSize']
    total_bedrooms = request['totalBedrooms']

    # 1. Normalize units
    normalized = normalize_units(length_m, width_m)
    scale_x = normalized['scale_x']
    scale_y = normalized['scale_y']

    # 2. Distribute bedrooms across floors
    bedrooms_per_floor = distribute_bedrooms_across_floors(total_bedrooms, floors)

    all_rooms = []
    room_id_counter = 1

    # Generate each floor
    for floor in range(floors):
        # 3. Create structural elements FIRST (deterministic placement)
        structural_regions, bsp_zones = create_structural_elements(length_m, width_m, floors, floor)

        # 4. Get room requirements for this floor
        floor_requirements = get_floor_room_requirements(
            total_rooms, bedrooms_per_floor, floors, floor
        )

        # 5. Apply BSP only to predefined zones and assign room types zone by zone
        all_regions = structural_regions.copy()  # Start with structural elements
        bedrooms_assigned_this_floor = 0

        total_bsp_area = sum(z.w * z.h for z in bsp_zones)
        print(f"Total BSP area: {total_bsp_area}")
        for zone_idx, zone in enumerate(bsp_zones):
            # Calculate target rooms for this zone proportional to its area
            zone_area_ratio = (zone.w * zone.h) / total_bsp_area if total_bsp_area > 0 else 1.0 / len(bsp_zones)
            print(f"Zone area ratio: {zone_area_ratio} for zone {zone_idx} in floor {floor}")
            # Estimate rooms needed (considering structural elements take space)
            # Reserve some rooms for structural elements (hallways, stairs, etc.)
            # Use a more conservative approach to avoid over-generation
            # structural_reserve = max(1, floors)  # Reserve at least 1 room per floor for structural elements
            # available_rooms_for_bsp = max(1, total_rooms - structural_reserve)

            target_rooms = max(1, int(total_rooms * zone_area_ratio / floors))
            print(f"Target rooms: {target_rooms} for zone {zone_idx} in floor {floor}")
            # Generate BSP regions
            zone_regions = split_space(zone, target_rooms, min_room_length, min_room_width, scale_x, scale_y)

            # Assign room types following new order
            zone_regions, bedrooms_assigned = assign_room_types_to_zone(
                zone_regions, floor, floors, zone_idx, floor_requirements,
                bedrooms_assigned_this_floor, scale_x, scale_y
            )
            bedrooms_assigned_this_floor += bedrooms_assigned

            all_regions.extend(zone_regions)

        # Ensure all regions have types (fallback for any unassigned BSP regions)
        for region in all_regions:
            if region.room_type is None:
                if floor > 0:  # Upper floors can have LIVING rooms
                    region.room_type = 'LIVING'
                else:
                    region.room_type = 'LIVING'  # Allow on ground floor as fallback

        # Convert to room dictionaries
        for region in all_regions:
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
