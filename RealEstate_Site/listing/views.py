from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsAdminRole
from .serializers import PropertySerializer
from .models import Property, Favorite
import locations.signals
from .hash_map import favorites_map

@api_view(['POST'])
@permission_classes([AllowAny])
def add_property(request):
    data = request.data    
    serializer = PropertySerializer(data=data)

    if serializer.is_valid():
        new_property = serializer.save()
        
        from .trees import property_tree,size_tree
        from .heap import cheap_heap,size_heap
        
        property_tree.insert(new_property)
        size_tree.insert(new_property)
        cheap_heap.insert(new_property)
        size_heap.insert(new_property)
        
        
        return Response({
            "message": "Property added",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_properties(request):
    data = Property.objects.all()
    serializer = PropertySerializer(data,many=True)    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET']) 
@permission_classes([AllowAny])
def search_price_range(request):
    try:
        min_p = float(request.query_params.get('min', 0))
        max_p = float(request.query_params.get('max', 999999999))
    except ValueError:
        return Response({"error": "Invalid price parameters"}, status=400)
    
    from .trees import property_tree
    
    results = property_tree.search_by_price_range(min_p, max_p)
    
    serializer = PropertySerializer(results, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_sorted_by_price(request):
    from .trees import property_tree
    
    data = property_tree.get_all_sorted()
    serializer = PropertySerializer(data,many=True)    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_sorted_by_size(request):
    from .trees import size_tree
    
    data = size_tree.get_all_sorted()
    serializer = PropertySerializer(data,many=True)    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def advanced_search(request):
    
    min_p = float(request.query_params.get('min_price', 0))
    max_p = float(request.query_params.get('max_price', 999999999))
    
    min_s = int(request.query_params.get('min_size', 0))
    max_s = int(request.query_params.get('max_size', 999999999))
    
    min_bed = int(request.query_params.get('min_bedrooms', 0))

    from .trees import property_tree
    initial_candidates = property_tree.search_by_price_range(min_p, max_p)

    filtered_results = []
    for prop in initial_candidates:
        size_ok = min_s <= prop.size <= max_s
        bed_ok = prop.bedrooms >= min_bed
        
        if size_ok and bed_ok:
            filtered_results.append(prop)

    from .serializers import PropertySerializer
    serializer = PropertySerializer(filtered_results, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request):
    user_id = request.user.id
    property_id = request.data.get('property_id')

    if not property_id:
        return Response({"error": "property_id is required"}, status=400)

    try:
        if not Property.objects.filter(id=property_id).exists():
            return Response({"error": "Property not found"}, status=404)

        if favorites_map.is_favorite(user_id, property_id):
            Favorite.objects.filter(user_id=user_id, property_id=property_id).delete()
            return Response({
                "message": "Removed from favorites",
                "is_favorite": False
            }, status=status.HTTP_200_OK)
        
        else:
            Favorite.objects.get_or_create(user_id=user_id, property_id=property_id)
            return Response({
                "message": "Added to favorites",
                "is_favorite": True
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_favorites(request):
    user_id = request.user.id
    
    fav_property_ids = favorites_map.get_all_for_user(user_id)

    if not fav_property_ids:
        return Response([], status=200)

    properties = Property.objects.filter(id__in=fav_property_ids)
    
    serializer = PropertySerializer(properties, many=True)
    return Response(serializer.data)