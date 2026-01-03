#!/usr/bin/env python3

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.join(os.getcwd(), 'RealEstate_Site'))

# Test the BSP parameter usage
try:
    from RealEstate_Site.homebuilder.services.bsp import split_space, BSPNode, normalize_units

    print("Testing BSP parameter usage...")

    # Test with different min room sizes
    test_cases = [
        {"min_length": 15, "min_width": 15, "desc": "15x15 meter minimums"},
        {"min_length": 20, "min_width": 25, "desc": "20x25 meter minimums"},
        {"min_length": 10, "min_width": 12, "desc": "10x12 meter minimums"},
    ]

    # Create a test zone
    zone = BSPNode(0, 0, 100, 100, 0)  # 100x100 internal units

    for case in test_cases:
        print(f"\n--- Testing {case['desc']} ---")

        # Get scale factors (assuming 100m x 100m house)
        normalized = normalize_units(100, 100)
        scale_x = normalized['scale_x']  # meters per internal unit
        scale_y = normalized['scale_y']

        print(f"Scale factors: x={scale_x:.3f}, y={scale_y:.3f}")
        print(f"Min room size in internal units: width={case['min_width']/scale_x:.1f}, length={case['min_length']/scale_y:.1f}")

        # Split the space
        regions = split_space(zone, 4, case['min_length'], case['min_width'], scale_x, scale_y)

        print(f"Generated {len(regions)} regions:")

        for i, region in enumerate(regions):
            # Convert back to meters for display
            width_m = region.w * scale_x
            height_m = region.h * scale_y
            print(f"  Region {i}: ({region.x:.1f}, {region.y:.1f}) {width_m:.1f}m x {height_m:.1f}m")
        # Check if all regions meet minimum requirements
        min_width_internal = case['min_width'] / scale_x
        min_height_internal = case['min_length'] / scale_y

        all_valid = all(
            region.w >= min_width_internal and region.h >= min_height_internal
            for region in regions
        )

        print(f"All regions meet minimum size requirements: {all_valid}")

    print("\n✓ BSP parameter testing completed successfully!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
