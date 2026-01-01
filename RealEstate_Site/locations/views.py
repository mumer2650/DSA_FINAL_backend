from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from listing.models import Property
from listing.serializers import PropertySerializer
from .models import Facility, Location, WayPoint,Connection
from .serializers import FacilitySerializer, BulkFacilitySerializer
from django.db import transaction
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def get_nearby_facilities(request, prop_id):
    try:
        try:
            target_property = Property.objects.get(id=prop_id)
            start_location_id = target_property.location_id.id
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
def get_all_facilities(request):
    facilities = Facility.objects.all()
    serialized = FacilitySerializer(facilities,many=True)
    return Response({"data":serialized.data},status=status.HTTP_200_OK)


# @api_view(['GET'])
# def get_shortest_path_distance(request):
#     from_id = request.query_params.get('from_id')
#     to_id = request.query_params.get('to_id')

#     if not from_id or not to_id:
#         return Response(
#             {"error": "Please provide both from_id and to_id"}, 
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     try:
#         from_id = int(from_id)
#         to_id = int(to_id)
        
#         from .graphs import graph

#         if not graph:
#             return Response(
#                 {"error": "Graph is not initialized"}, 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
            
#         result = graph.dijkstra_shortest_path(from_id,to_id)
#         distance = result['distance']
#         path_ids = result['path']

#         if distance == float('inf'):
#             return Response(
#                 {"error": "No path exists between these locations"}, 
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         edges = [
#             {"from_id": path_ids[i], "to_id": path_ids[i+1]} 
#             for i in range(len(path_ids) - 1)
#         ]
        
#         loc_objs = Location.objects.filter(id__in=path_ids)
#         loc_map = {loc.id: {"location_id": loc.id,"lat": loc.latitude, "lng": loc.longitude} for loc in loc_objs}
        
#         coordinates = [loc_map[node_id] for node_id in path_ids]

#         return Response({
#             "origin": graph.nodes_data[from_id]['name'],
#             "destination": graph.nodes_data[to_id]['name'],
#             "shortest_distance_km": distance,
#             "path_nodes": path_ids,
#             "nodes": coordinates,
#             "edges": edges,
#             "unit": "kilometers"
#         }, status=status.HTTP_200_OK)
#     except ValueError:
#         return Response({"error": "IDs must be integers"}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        # --- SMART LOGIC START ---
        # 1. Try to interpret 'from_id' as a Property ID first
        try:
            # We look for a property with this ID (e.g., 77)
            property_obj = Property.objects.get(id=from_id)
            
            # If found, we swap '77' for the actual Location ID (e.g., 12356291518)
            # Using the same field access pattern found in your 'get_nearby_facilities' view:
            if hasattr(property_obj, 'location_id'):
                # Checks if it's an object or an ID. 
                # If your model field is named 'location_id', this gets the object, then .id gets the int
                if hasattr(property_obj.location_id, 'id'):
                    from_id = property_obj.location_id.id
                else:
                    # Fallback if it was just an ID
                    from_id = property_obj.location_id
            elif hasattr(property_obj, 'location'):
                 from_id = property_obj.location.id
                 
            print(f"DEBUG: Translated Property ID {request.query_params.get('from_id')} to Location ID {from_id}")

        except Property.DoesNotExist:
            # It wasn't a Property ID, so it must be a raw Location ID already.
            pass
        # --- SMART LOGIC END ---
        
        from .graphs import graph

        if not graph:
            return Response(
                {"error": "Graph is not initialized"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        result = graph.dijkstra_shortest_path(from_id, to_id)
        distance = result['distance']
        path_ids = result['path']

        if distance == float('inf'):
            return Response(
                {"error": "No path exists between these locations"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        edges = [
            {"from_id": path_ids[i], "to_id": path_ids[i+1]} 
            for i in range(len(path_ids) - 1)
        ]
        
        loc_objs = Location.objects.filter(id__in=path_ids)
        loc_map = {loc.id: {"location_id": loc.id,"lat": loc.latitude, "lng": loc.longitude} for loc in loc_objs}
        
        # Ensure strict ordering of coordinates matching the path
        coordinates = []
        for node_id in path_ids:
            if node_id in loc_map:
                coordinates.append(loc_map[node_id])
            else:
                # Fallback if a node is missing from DB (shouldn't happen)
                continue

        return Response({
            "origin": graph.nodes_data.get(from_id, {}).get('name', 'Unknown'),
            "destination": graph.nodes_data.get(to_id, {}).get('name', 'Unknown'),
            "shortest_distance_km": distance,
            "path_nodes": path_ids,
            "nodes": coordinates,
            "edges": edges,
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
        all_properties = Property.objects.all()
    except Property.DoesNotExist:
        return Response({"error": "Property not found"}, status=status.HTTP_404_NOT_FOUND)
    
    from .graphs import RecomendationGraph
    recommended = RecomendationGraph()
    recommended.generate_similarity_graph(all_properties)
    similar_ids = recommended.bfs_traversal(prop_id)
    
    results = []
    for sid in similar_ids:
        p = Property.objects.get(id=sid)
        results.append(p)
        
    serialized = PropertySerializer(results,many=True)

    return Response({
        "target_property": target_property.title,
        "recommendations": serialized.data
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

    properties = [item[1] for item in extracted_items]
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

    properties = [item[1] for item in extracted_items]
    serializer = PropertySerializer(properties, many=True)

    for prop in properties:
        size_heap.insert(prop)

    return Response({
        "count": len(serializer.data),
        "largest_properties": serializer.data
    }, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def bulk_add_waypoints(request):
    waypoint_data_list = request.data  
    
    try:
        with transaction.atomic():  
            for item in waypoint_data_list:
                loc = Location.objects.create(
                    #id=item['id'],
                    name=item['name'],
                    latitude=item['lat'],
                    longitude=item['long'],
                    location_type='way_point'
                )
                
                WayPoint.objects.create(
                    location=loc,
                    node_type=item['waypoint_type']
                )
                
        return Response({"message": f"Successfully added {len(waypoint_data_list)} waypoints"}, status=201)
    
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
@api_view(['POST'])
def bulk_connection_upload(request):
    if not isinstance(request.data, list):
        return Response({"error": "Expected a list."}, status=400)

    created_count = 0
    errors = []

    for item in request.data:
        from_id = item.get('from_location')
        to_id = item.get('to_location')
        
        try:

            obj, created = Connection.objects.get_or_create(
                from_location_id=from_id, 
                to_location_id=to_id
            )
            if created:
                created_count += 1
        except Exception as e:
            errors.append({"pair": f"{from_id}-{to_id}", "error": str(e)})

    return Response({
        "message": f"Processed batch. {created_count} new connections created.",
        "errors": errors
    }, status=201)
 
@api_view(['POST'])
def bulk_add_facilities(request):
    data = request.data
    
    if not isinstance(data, list):
        return Response({"error": "Expected a list of facility objects"}, status=status.HTTP_400_BAD_REQUEST)

    created_facilities = []
    
    try:
        with transaction.atomic():
            for item in data:
                serializer = BulkFacilitySerializer(data=item)
                if serializer.is_valid():
                    new_facility = serializer.save()
                    
                    
                    created_facilities.append(serializer.data)
                else:
                    raise ValueError(f"Error in {item.get('name')}: {serializer.errors}")

        return Response({
            "message": f"Successfully added {len(created_facilities)} facilities and updated road network.",
            "count": len(created_facilities)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
def delete_location_and_property(request, pk):
    try:
        location = Location.objects.get(pk=pk)
        try:
            prop = location.property 
         
            
        except Property.DoesNotExist:
            prop = None
        location.delete()

        return Response({
            "message": f"Location {pk} and its associated property were deleted successfully."
        }, status=status.HTTP_200_OK)

    except Location.DoesNotExist:
        return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)