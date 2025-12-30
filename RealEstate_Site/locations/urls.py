from django.urls import path
from .views import get_nearby_facilities,get_shortest_path_distance, get_similar_recomendations,get_largest_sizes,get_top_cheepest,get_all_facilities,bulk_add_waypoints, bulk_connection_upload, bulk_add_facilities


urlpatterns = [
    path('nearby/<int:prop_id>/', get_nearby_facilities, name='nearby-facilities'),
    path('shortest-path/',get_shortest_path_distance, name= 'shortest-path'),
    path('recommendations/<int:prop_id>/',get_similar_recomendations, name= 'similar-properties'),
    path('k-cheapest/',get_top_cheepest, name= 'cheap-properties'),
    path('k-largest/',get_largest_sizes, name= 'large-properties'),
    path('get-facilities/',get_all_facilities, name= 'all_facilities'),
    path('add-way-point/',bulk_add_waypoints, name = "add-way-point") ,  
    path('add-connection/',bulk_connection_upload, name = "add-connection") ,  
    path('add-facilities/',bulk_add_facilities, name = "add-facilities") ,  
]