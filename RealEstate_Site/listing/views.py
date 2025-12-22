from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsAdminRole
from .serializers import PropertySerializer
from .models import Property

@api_view(['POST'])
@permission_classes([AllowAny])
def add_property(request):
    data = request.data    
    serializer = PropertySerializer(data=data)
    
    
    if serializer.is_valid():
        new_property = serializer.save()
        
        from .trees import property_tree
        property_tree.insert(new_property)
        
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