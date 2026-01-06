import random
from collections import defaultdict, deque
from ..models import Room

class BSPNode:
    """
    BSPNode represents a rectangular space partition in 2D floor layout.
    Attributes:
        x, y: Top-left coordinates (percentage-based: 0-100)
        w, h: Width and height (percentage-based: 0-100)
        floor: Floor number (0-based)
        left, right: Child nodes from binary space partitioning
        room_type: Assigned room type (e.g., 'HALL', 'BEDROOM', etc.)
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
    return {
        "x": 0,
        "y": 0,
        "w": 100,
        "h": 100,
        "scale_x": length_m / 100,
        "scale_y": width_m / 100,
    }

def area_in_meters(region, scale_x, scale_y):
    return (region.w * scale_x) * (region.h * scale_y)

def detect_layout_case(length_m, width_m):
    if width_m > 70:
        return "DOUBLE_SIDED_HALL"
    elif width_m > 50:
        return "SINGLE_SIDED_HALL"
    else:
        return "COMPACT"

def create_structural_elements(length_m, width_m, floors, current_floor):
    layout_case = detect_layout_case(length_m, width_m)
    structural_regions = []
    bsp_zones = []
    is_ground_floor = (current_floor == 0)
    is_multi_floor = (floors > 1)

    if layout_case == "DOUBLE_SIDED_HALL":
        hallway_width_percent = 10
        hallway_width = hallway_width_percent

        if is_ground_floor:
            kdl_height_percent = 60
            bsp_height_percent = 40

            kdl_hub = BSPNode(
                x=0,
                y=0,
                w=45,
                h=kdl_height_percent,
                floor=current_floor
            )
            kdl_hub.room_type = "KITCHEN_LIVING_DINING_HUB"
            structural_regions.append(kdl_hub)

            hallway = BSPNode(
                x=kdl_hub.w,
                y=0,
                w=hallway_width,
                h=100,
                floor=current_floor
            )
            hallway.room_type = "HALL"
            structural_regions.append(hallway)

            if is_multi_floor:
                stair_height_percent = 20
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

            left_bsp = BSPNode(
                x=0,
                y=kdl_height_percent,
                w=45,
                h=bsp_height_percent,
                floor=current_floor
            )
            bsp_zones.append(left_bsp)

            right_bsp = BSPNode(
                x=hallway.x + hallway.w,
                y=0,
                w=45,
                h=100,
                floor=current_floor
            )
            bsp_zones.append(right_bsp)

        else:
            stair_height_percent = 20
            hallway = BSPNode(
                x=(100 - hallway_width) / 2,
                y=0,
                w=hallway_width,
                h=100-stair_height_percent,
                floor=current_floor
            )
            hallway.room_type = "HALL"
            structural_regions.append(hallway)

            if is_multi_floor:
                stairs = BSPNode(
                    x=hallway.x,
                    y=hallway.h,
                    w=hallway.w,
                    h=stair_height_percent,
                    floor=current_floor
                )
                stairs.room_type = "STAIR"
                structural_regions.append(stairs)

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
        hallway_width_percent = 20
        bsp_height_percent = 60

        if is_ground_floor:
            kdl_height_percent = 40

            hallway = BSPNode(
                x=0,
                y=0,
                w=hallway_width_percent,
                h=40,
                floor=current_floor
            )
            hallway.room_type = "HALL"
            structural_regions.append(hallway)

            kdl_hub = BSPNode(
                x=hallway_width_percent,
                y=0,
                w=80,
                h=kdl_height_percent,
                floor=current_floor
            )
            kdl_hub.room_type = "KITCHEN_LIVING_DINING_HUB"
            structural_regions.append(kdl_hub)

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

            bsp_zone = BSPNode(
                x=0,
                y=kdl_height_percent,
                w=100,
                h=bsp_height_percent,
                floor=current_floor
            )
            bsp_zones.append(bsp_zone)

        else:
            hallway_height_percent = 40
            hallway = BSPNode(
            x=hallway_width_percent,
            y=0,
            w=80,
            h=hallway_height_percent,
            floor=current_floor
            )
            hallway.room_type = "HALL"
            structural_regions.append(hallway)

            if is_multi_floor:
                stairs = BSPNode(
                x=0,
                y=0,
                w=hallway_width_percent,
                h=40,
                floor=current_floor
                )
                stairs.room_type = "STAIR"
                structural_regions.append(stairs)

            bsp_zone = BSPNode(
                x=0,
                y=hallway_height_percent,
                w=100,
                h=bsp_height_percent,
                floor=current_floor
            )
            bsp_zones.append(bsp_zone)

    else:
        if is_ground_floor:
            kdl_height_percent = 40
            bsp_height_percent = 60

            kdl_hub = BSPNode(
                x=0,
                y=0,
                w=100,
                h=kdl_height_percent,
                floor=current_floor
            )
            kdl_hub.room_type = "KITCHEN_LIVING_DINING_HUB"
            structural_regions.append(kdl_hub)

            if is_multi_floor:
                stair_width_percent = 20
                stair_height_percent = 40
                stairs = BSPNode(
                    x=0,
                    y=0,
                    w=stair_width_percent,
                    h=stair_height_percent,
                    floor=current_floor
                )
                stairs.room_type = "STAIR"
                structural_regions.append(stairs)

                kdl_hub.x = stair_width_percent
                kdl_hub.w = 100 - stair_width_percent

            bsp_zone = BSPNode(
                x=0,
                y=kdl_height_percent,
                w=100,
                h=bsp_height_percent,
                floor=current_floor
            )
            bsp_zones.append(bsp_zone)

        else:
            stair_hall_width_percent = 20
            upper_bsp_width_percent = 60
            stair_hall_height_percent = 40

            stairs = BSPNode(
                x=0,
                y=0,
                w=stair_hall_width_percent,
                h=stair_hall_height_percent,
                floor=current_floor
            )
            stairs.room_type = "STAIR"
            structural_regions.append(stairs)

            hallway = BSPNode(
                x=stair_hall_width_percent,
                y=0,
                w=stair_hall_width_percent,
                h=stair_hall_height_percent,
                floor=current_floor
            )
            hallway.room_type = "HALL"
            structural_regions.append(hallway)

            upper_bsp_zone = BSPNode(
                x=stair_hall_width_percent + stair_hall_width_percent,
                y=0,
                w=upper_bsp_width_percent,
                h=stair_hall_height_percent,
                floor=current_floor
            )
            bsp_zones.append(upper_bsp_zone)

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
    if floors == 1:
        return [total_bedrooms]

    bedrooms_per_floor = [0] * floors

    ground_floor_bedrooms = max(1, total_bedrooms // (floors + 1))
    bedrooms_per_floor[0] = ground_floor_bedrooms

    remaining_bedrooms = total_bedrooms - ground_floor_bedrooms
    upper_floor_bedrooms = remaining_bedrooms // (floors - 1)
    remainder = remaining_bedrooms % (floors - 1)

    for i in range(1, floors):
        bedrooms_per_floor[i] = upper_floor_bedrooms
        if i - 1 < remainder:
            bedrooms_per_floor[i] += 1

    max_upper = max(bedrooms_per_floor[1:]) if floors > 1 else 0
    if bedrooms_per_floor[0] > max_upper and max_upper > 0:
        extra = bedrooms_per_floor[0] - max_upper
        bedrooms_per_floor[0] = max_upper

        for i in range(1, floors):
            if extra > 0:
                bedrooms_per_floor[i] += 1
                extra -= 1
                if extra == 0:
                    break
    
    print(f"Distributed bedrooms per floor: {bedrooms_per_floor}")

    return bedrooms_per_floor


def get_floor_room_requirements(total_rooms, bedrooms_per_floor, floors, current_floor):
    requirements = {
        'ATTACHED_BED_BATH': bedrooms_per_floor[current_floor],
        'STUDYROOM': 0,
        'STORAGE': 0,
        'LIVING': 0
    }

    if current_floor == 0:
            requirements['STUDYROOM'] = 1
            requirements['STORAGE'] = 1
    else:
        if floors >= 3 and current_floor == floors - 1:
            requirements['STORAGE'] = 1

    if current_floor > 0:
        remaining_house_rooms = total_rooms - sum(bedrooms_per_floor)
        if floors > 1:
            living_per_upper_floor = remaining_house_rooms // (floors - 1)
            used_slots = (requirements['ATTACHED_BED_BATH'] +
                         requirements['STUDYROOM'] +
                         requirements['STORAGE'])
            requirements['LIVING'] = max(0, living_per_upper_floor - used_slots)

    return requirements


def assign_kitchen(regions, scale_x, scale_y, kitchen_area):
    floor_0_regions = [r for r in regions if r.floor == 0 and r.room_type is None]

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
    unassigned = sorted([r for r in zone_regions if r.room_type is None],
                        key=lambda r: r.w * r.h)

    bedrooms_assigned_to_zone = 0

    if floor == 0:
        if floor_requirements['STUDYROOM'] > 0 and unassigned:
            region = unassigned.pop(0)
            region.room_type = 'STUDYROOM'
            floor_requirements['STUDYROOM'] -= 1

        if floor_requirements['STORAGE'] > 0 and unassigned:
            region = unassigned.pop(0)
            region.room_type = 'STORAGE'
            floor_requirements['STORAGE'] -= 1

        bedrooms_needed = floor_requirements['ATTACHED_BED_BATH'] - bedrooms_assigned
        bedrooms_to_assign = min(bedrooms_needed, len(unassigned))

        for i in range(bedrooms_to_assign):
            if unassigned:
                region = unassigned.pop(0)
                region.room_type = 'ATTACHED_BED_BATH'
                bedrooms_assigned_to_zone += 1
    else:
        bedrooms_needed = floor_requirements['ATTACHED_BED_BATH'] - bedrooms_assigned
        bedrooms_to_assign = min(bedrooms_needed, len(unassigned))

        for i in range(bedrooms_to_assign):
            if unassigned:
                region = unassigned.pop(0)
                region.room_type = 'ATTACHED_BED_BATH'
                bedrooms_assigned_to_zone += 1

        if floor_requirements['STUDYROOM'] > 0 and unassigned:
            region = unassigned.pop(0)
            region.room_type = 'STUDYROOM'
            floor_requirements['STUDYROOM'] -= 1

        if floor_requirements['STORAGE'] > 0 and unassigned:
            region = unassigned.pop(0)
            region.room_type = 'STORAGE'
            floor_requirements['STORAGE'] -= 1
        isKitchenAssigned = False
    for region in unassigned:
        print(f"Unassigned region on floor {floor}, zone {zone_idx}: {region.w}x{region.h}")
        if floor > 0:
            region.room_type = 'LIVING'
        else:
            region.room_type = None

    return zone_regions, bedrooms_assigned_to_zone



def split_space(node, target_leaves, min_room_length_m, min_room_width_m, scale_x, scale_y, layout_case):
    print(f"split_space called: zone size {node.w}x{node.h}, target_leaves={target_leaves}")

    min_room_width_internal = min_room_width_m / scale_x
    min_room_length_internal = min_room_length_m / scale_y

    leaves = [node]

    min_room_area = min_room_width_internal * min_room_length_internal
    max_possible = min(target_leaves, max(1, int((node.w * node.h) / (min_room_area * 2))))
    actual_target = min(target_leaves, max_possible)

    max_iterations = 100
    iterations = 0

    while len(leaves) < actual_target and iterations < max_iterations:
        iterations += 1
        if not leaves:
            break

        leaf = leaves.pop(0)

        if(layout_case == "DOUBLE_SIDED_HALL"):
            print("  DOUBLE_SIDED_HALL layout - applying relaxed splitting criteria")
            if leaf.w < min_room_width_internal * 1.8 or leaf.h < min_room_length_internal * 1.8:
                leaves.append(leaf)
                continue
        else:
            if leaf.w < min_room_width_internal * 2 or leaf.h < min_room_length_internal * 2:
                leaves.append(leaf)
                continue

        if leaf.w > leaf.h:
            split = random.uniform(0.4, 0.6)
            left = BSPNode(leaf.x, leaf.y, leaf.w * split, leaf.h, leaf.floor)
            right = BSPNode(leaf.x + leaf.w * split, leaf.y, leaf.w * (1 - split), leaf.h, leaf.floor)
        else:
            split = random.uniform(0.4, 0.6)
            left = BSPNode(leaf.x, leaf.y, leaf.w, leaf.h * split, leaf.floor)
            right = BSPNode(leaf.x, leaf.y + leaf.h * split, leaf.w, leaf.h * (1 - split), leaf.floor)

        leaves.extend([left, right])

    print(f"split_space returning {len(leaves)} leaves (target was {actual_target}, iterations: {iterations})")
    return leaves

def get_leaf_nodes(node):
    if node.left is None and node.right is None:
        return [node]

    leaves = []
    if node.left:
        leaves.extend(get_leaf_nodes(node.left))
    if node.right:
        leaves.extend(get_leaf_nodes(node.right))

    return leaves

def generate_house(request):
    length_m = request['length']
    width_m = request['width']
    floors = request['floors']
    total_rooms = request['rooms']
    min_room_length = request['minRoomLength']
    min_room_width = request['minRoomWidth']
    kitchen_area = request['kitchenSize']
    total_bedrooms = request['totalBedrooms']

    normalized = normalize_units(length_m, width_m)
    scale_x = normalized['scale_x']
    scale_y = normalized['scale_y']

    bedrooms_per_floor = distribute_bedrooms_across_floors(total_bedrooms, floors)

    all_rooms = []
    room_id_counter = 1

    for floor in range(floors):
        structural_regions, bsp_zones = create_structural_elements(length_m, width_m, floors, floor)

        floor_requirements = get_floor_room_requirements(
            total_rooms, bedrooms_per_floor, floors, floor
        )

        all_regions = structural_regions.copy()
        bedrooms_assigned_this_floor = 0

        total_bsp_area = sum(z.w * z.h for z in bsp_zones)
        print(f"Total BSP area: {total_bsp_area}")
        for zone_idx, zone in enumerate(bsp_zones):
            zone_area_ratio = (zone.w * zone.h) / total_bsp_area if total_bsp_area > 0 else 1.0 / len(bsp_zones)
            print(f"Zone area ratio: {zone_area_ratio} for zone {zone_idx} in floor {floor}")

            # structural_reserve = max(1, floors)
            # available_rooms_for_bsp = max(1, total_rooms - structural_reserve)

            target_rooms = max(1, int(total_rooms * zone_area_ratio / floors))
            print(f"Target rooms: {target_rooms} for zone {zone_idx} in floor {floor}")
            zone_regions = split_space(zone, target_rooms, min_room_length, min_room_width, scale_x, scale_y, detect_layout_case(length_m, width_m) )

            zone_regions, bedrooms_assigned = assign_room_types_to_zone(
                zone_regions, floor, floors, zone_idx, floor_requirements,
                bedrooms_assigned_this_floor, scale_x, scale_y
            )
            bedrooms_assigned_this_floor += bedrooms_assigned

            all_regions.extend(zone_regions)

        for region in all_regions:
            if region.room_type is None:
                if floor > 0:
                    region.room_type = 'LIVING'
                elif floor == floors - 1:
                    region.room_type = 'KITCHEN'
                else:
                    region.room_type = 'LIVING'

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

