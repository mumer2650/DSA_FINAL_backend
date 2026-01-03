#!/usr/bin/env python3

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.join(os.getcwd(), 'RealEstate_Site'))

# Test zone-based room assignment
try:
    from RealEstate_Site.homebuilder.services.bsp import (
        assign_room_types_to_zone, get_floor_room_requirements, BSPNode
    )

    print("Testing zone-based room assignment...")

    # Create mock regions for a zone
    regions = [
        BSPNode(0, 0, 50, 50, 0),    # Large room
        BSPNode(50, 0, 30, 30, 0),   # Medium room
        BSPNode(0, 50, 25, 25, 0),   # Small room
    ]

    print("Created 3 mock regions in zone")

    # Test ground floor (should get kitchen)
    floor_assignments = []
    result_regions = assign_room_types_to_zone(
        regions, 0, 2, 0, floor_assignments, 1.0, 1.0, 250, 100, True
    )

    print(f"Ground floor zone assignments: {floor_assignments}")
    for i, region in enumerate(result_regions):
        print(f"  Region {i}: {region.room_type}")

    print("\n" + "="*50 + "\n")

    # Test upper floor
    regions2 = [
        BSPNode(0, 0, 40, 40, 1),    # Large room
        BSPNode(40, 0, 35, 35, 1),   # Medium room
    ]

    floor_assignments2 = []
    result_regions2 = assign_room_types_to_zone(
        regions2, 1, 2, 0, floor_assignments2, 1.0, 1.0, 250, 100, False
    )

    print(f"Upper floor zone assignments: {floor_assignments2}")
    for i, region in enumerate(result_regions2):
        print(f"  Region {i}: {region.room_type}")

    print("\n✓ Zone-based assignment test completed!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
