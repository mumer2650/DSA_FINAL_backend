#!/usr/bin/env python3

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.join(os.getcwd(), 'RealEstate_Site'))

# Test the layout generation
try:
    from RealEstate_Site.homebuilder.services.bsp import detect_layout_case, create_structural_elements

    print("Testing layout case detection...")
    case = detect_layout_case(100, 100)
    print(f"100x100 -> {case}")

    case2 = detect_layout_case(50, 50)
    print(f"50x50 -> {case2}")

    print("\nTesting structural elements creation...")
    structural, zones = create_structural_elements(100, 100, 1, 0)
    print(f"Created {len(structural)} structural regions and {len(zones)} BSP zones")

    for i, elem in enumerate(structural):
        print(f"  Structural {i}: {elem.room_type}")

    for i, zone in enumerate(zones):
        print(f"  BSP Zone {i}: {zone.w}x{zone.h}")

    print("\nSUCCESS: Basic layout functions work!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
