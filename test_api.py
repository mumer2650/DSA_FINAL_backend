#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RealEstate_Site.RealEstate_Site.settings')
sys.path.insert(0, os.path.join(os.getcwd(), 'RealEstate_Site'))
django.setup()

print('Testing layout generation directly...')
from RealEstate_Site.homebuilder.services.bsp import generate_house

request = {
    'length': 100,
    'width': 100,
    'floors': 1,
    'rooms': 4,
    'minRoomLength': 15,
    'minRoomWidth': 15,
    'kitchenSize': 250,
    'washroomSize': 100
}

try:
    layout = generate_house(request)
    print(f'SUCCESS! Generated {len(layout["rooms"])} rooms')
    for room in layout['rooms'][:5]:  # Show first 5 rooms
        print(f'  {room["type"]}: ({room["x"]:.1f}, {room["y"]:.1f}) {room["width"]:.1f}x{room["height"]:.1f}')
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
