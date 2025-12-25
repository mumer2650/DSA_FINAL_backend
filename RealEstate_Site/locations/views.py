from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from listing.models import Property

@api_view(['GET'])
def get_nearby_facilities(request, prop_id):
    try:
        try:
            target_property = Property.objects.get(id=prop_id)
            start_location_id = target_property.location_id 
        except Property.DoesNotExist:
            return Response({"error": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

        from .graphs import graph

        if not graph:
            return Response({"error": "Graph not initialized"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        max_dist = float(request.query_params.get('radius', 5.0))
        nearby_facilities = graph.bfs_nearby_facilities(start_location_id, max_dist)

        return Response({
            "property_name": target_property.title,
            "search_radius": {max_dist},
            "total_found": len(nearby_facilities),
            "facilities": nearby_facilities
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_shortest_path_distance(request):
    from_id = request.query_params.get('from_id')
    to_id = request.query_params.get('to_id')

    if not from_id or not to_id:
        return Response(
            {"error": "Please provide both from_id and to_id"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        from_id = int(from_id)
        to_id = int(to_id)
        
        from .graphs import graph

        if not graph:
            return Response(
                {"error": "Graph is not initialized"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        distance = graph.dijkstra_shortest_path(from_id,to_id)

        if distance == float('inf'):
            return Response(
                {"error": "No path exists between these locations"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            "origin": graph.nodes_data[from_id]['name'],
            "destination": graph.nodes_data[to_id]['name'],
            "shortest_distance_km": distance,
            "unit": "kilometers"
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({"error": "IDs must be integers"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_similar_recomendations(request,prop_id):
    try:
        target_property = Property.objects.get(id=prop_id)
    except Property.DoesNotExist:
        return Response({"error": "Property not found"}, status=status.HTTP_404_NOT_FOUND)
    
    from .graphs import RecomendationGraph
    recommended = RecomendationGraph()
    recommended.generate_similarity_graph(target_property)
    similar_ids = recommended.bfs_recommendations(prop_id)
    
    results = []
    for sid in similar_ids:
        p = Property.objects.get(id=sid)
        results.append(p)

    return Response({
        "target_property": target_property.name,
        "recommendations": results
    }, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def get_top_cheepest(request):
    from listing.heap import cheap_heap
    from listing.serializers import PropertySerializer
    try:
        total_str = request.query_params.get('required-cheapest', 5)
        total = int(total_str)
    except ValueError:
        return Response({"error": "required-cheapest must be an integer"}, status=400)

    count = min(total, len(cheap_heap))
    
    extracted_items = []
    
    for _ in range(count):
        item = cheap_heap.extract_min()
        if item:
            extracted_items.append(item)

    properties = [item[2] for item in extracted_items]
    serializer = PropertySerializer(properties, many=True)

    for prop in properties:
        cheap_heap.insert(prop)

    return Response({
        "count": len(serializer.data),
        "cheapest_properties": serializer.data
    }, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def get_largest_sizes(request):
    from listing.heap import size_heap
    from listing.serializers import PropertySerializer
    try:
        total_str = request.query_params.get('required-largest', 5)
        total = int(total_str)
    except ValueError:
        return Response({"error": "required-cheapest must be an integer"}, status=400)

    count = min(total, len(size_heap))
    
    extracted_items = []
    
    for _ in range(count):
        item = size_heap.extract_max()
        if item:
            extracted_items.append(item)

    properties = [item[2] for item in extracted_items]
    serializer = PropertySerializer(properties, many=True)

    for prop in properties:
        size_heap.insert(prop)

    return Response({
        "count": len(serializer.data),
        "largest_properties": serializer.data
    }, status=status.HTTP_200_OK)