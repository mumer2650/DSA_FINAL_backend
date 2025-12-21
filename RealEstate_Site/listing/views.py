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

