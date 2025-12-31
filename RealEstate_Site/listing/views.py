from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsAdminRole
from .serializers import PropertySerializer, PropertyRequestSerializer
from .models import Property, Favorite, PropertyRequest
import locations.signals
from django.db import transaction
from .hash_map import favorites_map
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

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

@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_add_properties(request):
    data = request.data
    
    if not isinstance(data, list):
        return Response({"error": "Expected a list of property objects"}, status=status.HTTP_400_BAD_REQUEST)

    created_properties = []
    
    try:
        with transaction.atomic():
            
            from .trees import property_tree, size_tree
            from .heap import cheap_heap, size_heap

            for property_data in data:
                serializer = PropertySerializer(data=property_data)
                
                if serializer.is_valid():
                    
                    new_property = serializer.save()
                    
                    
                    property_tree.insert(new_property)
                    size_tree.insert(new_property)
                    cheap_heap.insert(new_property)
                    size_heap.insert(new_property)
                    
                    created_properties.append(serializer.data)
                else:
                    raise ValueError(f"Validation failed for {property_data.get('title', 'Unknown')}: {serializer.errors}")

        return Response({
            "message": f"Successfully added {len(created_properties)} properties",
            "data": created_properties
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny]) 
def get_single_property_detail(request, prop_id):
    try:
        property_obj = get_object_or_404(Property, id=prop_id)
        
        if request.user.is_authenticated:
            from .hash_map import recent_view
            recent_view.add_view(request.user.id, prop_id)

        serializer = PropertySerializer(property_obj)
        
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def property_keyword_search(request):
    query = request.query_params.get('q', '')

    if not query:
        return Response({"error": "Please provide a search keyword"}, status=400)

    properties = Property.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )

    serializer = PropertySerializer(properties, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_properties(request):
    data = Property.objects.all()
    serializer = PropertySerializer(data,many=True)    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_featured_properties(request):
    
    featured_props = Property.objects.filter(is_featured=True).order_by('-created_at')
    
    if not featured_props.exists():
        return Response({"message": "No featured properties found"}, status=200)

    serializer = PropertySerializer(featured_props, many=True)
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def property_view(request):
    user_id = request.user.id
    property_id = request.data.get('property_id')

    if not property_id:
        return Response({"error": "property_id is required"}, status=400)

    try:
        try:
            prop = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"error": "Property not found"}, status=404)

        from .hash_map import recent_view
        recent_view.add_view(user_id,property_id)
        
        serializer = PropertySerializer(prop)
        return Response({
            "message": "View recorded in stack",
            "property": serializer.data
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_list(request):
    user_id = request.user.id
    from .hash_map import recent_view
    recent_ids = recent_view.get_history(user_id)
    
    properties = []
    
    for prop_id in recent_ids:
        prop = Property.objects.filter(id=prop_id).first()
        if prop:
            properties.append(prop) 
            
    serializer = PropertySerializer(properties, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_searches(request):
    user_id = request.user.id
    from .hash_map import search_cache
    recent_searches = search_cache.get_search_history(user_id)
    

    return Response({"search_history" : recent_searches}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_property_request(request):
    """
    Expected JSON: {"property": 15, "request_type": "buy"}
    """
    serializer = PropertyRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            serializer.save(user=request.user)
            return Response({
                "message": "Request submitted successfully!",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except IntegrityError:
            return Response({
                "error": "You have already submitted a request for this property."
            }, status=status.HTTP_400_BAD_REQUEST)
            
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_requests(request):
    """
    Returns requests based on user role.
    Admins see all, Customers see only their own.
    """
    user = request.user

    requests = PropertyRequest.objects.all().order_by('-created_at')

    serializer = PropertyRequestSerializer(requests, many=True)
    
    return Response({
        "count": len(serializer.data),
        "requests": serializer.data
    })

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def manage_property_request(request, request_id):
    """
    Body: {"action": "approve"} OR {"action": "reject"}
    """
    if request.user.role != 'admin':
        return Response(
            {"error": "Unauthorized. Only admins can perform this action."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    prop_request = get_object_or_404(PropertyRequest, id=request_id)

    action = request.data.get('action')

    if action == 'approve':
        prop_request.status = 'approved'
    elif action == 'reject':
        prop_request.status = 'rejected'
    else:
        return Response(
            {"error": "Invalid action. Use 'approve' or 'reject'."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    prop_request.save()

    return Response({
        "message": f"Request {request_id} has been {prop_request.status}.",
        "request_id": prop_request.id,
        "new_status": prop_request.status
    }, status=status.HTTP_200_OK)