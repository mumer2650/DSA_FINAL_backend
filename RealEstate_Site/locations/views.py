from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from listing.models import Property

@api_view(['GET'])
def get_nearby_facilities(request, prop_id):
    try:
        try:
            target_property = Property.objects.get(id=prop_id)
            start_location_id = target_property.location.id 
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