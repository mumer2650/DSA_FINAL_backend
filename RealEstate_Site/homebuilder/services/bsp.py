import random
from collections import defaultdict
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


def generate_floor_layout(floor_no, length, width, target_rooms, min_room_size=20, max_room_size=40):
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
    split_space(root, target_rooms, min_room_size, max_room_size)

    # Collect leaf nodes as rooms
    leaf_nodes = get_leaf_nodes(root)

    # Assign room types based on rules
    assign_room_types(leaf_nodes, floor_no)

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


def split_space(node, target_rooms, min_room_size, max_room_size, depth=0):
    """
    Recursively split space using BSP algorithm.

    Args:
        node: Current BSP node to split
        target_rooms: Target number of rooms
        min_room_size: Minimum room size
        max_room_size: Maximum room size
        depth: Current recursion depth
    """
    # Stop splitting if we have enough rooms or reached minimum size
    if depth >= target_rooms - 1 or node.w < min_room_size * 2 or node.h < min_room_size * 2:
        return

    # Decide split orientation (horizontal or vertical)
    can_split_horizontal = node.h >= min_room_size * 2
    can_split_vertical = node.w >= min_room_size * 2

    if not can_split_horizontal and not can_split_vertical:
        return

    if can_split_horizontal and can_split_vertical:
        # Random choice with preference for vertical splits
        split_horizontal = random.choice([True, False, False])  # 33% horizontal, 67% vertical
    elif can_split_horizontal:
        split_horizontal = True
    else:
        split_horizontal = False

    if split_horizontal:
        # Split horizontally
        split_ratio = random.uniform(0.3, 0.7)  # Avoid very thin rooms
        split_pos = node.y + node.h * split_ratio

        node.left = BSPNode(node.x, node.y, node.w, node.h * split_ratio, node.floor)
        node.right = BSPNode(node.x, split_pos, node.w, node.h * (1 - split_ratio), node.floor)
    else:
        # Split vertically
        split_ratio = random.uniform(0.3, 0.7)
        split_pos = node.x + node.w * split_ratio

        node.left = BSPNode(node.x, node.y, node.w * split_ratio, node.h, node.floor)
        node.right = BSPNode(split_pos, node.y, node.w * (1 - split_ratio), node.h, node.floor)

    # Recurse on children
    split_space(node.left, target_rooms, min_room_size, max_room_size, depth + 1)
    split_space(node.right, target_rooms, min_room_size, max_room_size, depth + 1)


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


def assign_room_types(nodes, floor_no):
    """
    Assign room types to BSP leaf nodes based on rules.

    Args:
        nodes: List of leaf BSP nodes
        floor_no: Floor number
    """
    # Mandatory rooms per floor
    mandatory_rooms = []

    # Every floor needs at least 1 bedroom and 1 hallway
    mandatory_rooms.append('BEDROOM')
    mandatory_rooms.append('HALL')

    # Add stairway on all floors (same position across floors)
    mandatory_rooms.append('STAIR')

    # Assign mandatory rooms first
    assigned_count = 0
    for node in nodes:
        if assigned_count < len(mandatory_rooms):
            node.room_type = mandatory_rooms[assigned_count]
            assigned_count += 1
        else:
            break

    # Assign remaining rooms randomly from available types
    available_types = ['BEDROOM', 'KITCHEN', 'BATH', 'LIVING', 'HALL']
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


def generate_complete_house(length, width, floors, rooms_per_floor, min_room_size=20, max_room_size=40, kitchen_size=25, washroom_size=10):
    """
    Generate complete house layout across all floors.

    Args:
        length: House length
        width: House width
        floors: Number of floors
        rooms_per_floor: Target rooms per floor
        min_room_size: Minimum room size
        max_room_size: Maximum room size
        kitchen_size: Kitchen size preference
        washroom_size: Washroom size preference

    Returns:
        Dictionary with home layout data
    """
    all_rooms = []
    room_id_counter = 1

    # Generate each floor
    for floor in range(floors):
        floor_rooms = generate_floor_layout(floor, length, width, rooms_per_floor, min_room_size, max_room_size)

        # Adjust room IDs and add to complete list
        for room in floor_rooms:
            room['id'] = room_id_counter
            room_id_counter += 1

        all_rooms.extend(floor_rooms)

    # Apply global house rules
    apply_house_rules(all_rooms, floors)

    return {
        'length': length,
        'width': width,
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
