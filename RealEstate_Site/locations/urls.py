from django.urls import path
from .views import get_nearby_facilities,get_shortest_path_distance, get_similar_recomendations,get_largest_sizes,get_top_cheepest


urlpatterns = [
    path('nearby/<int:prop_id>/', get_nearby_facilities, name='nearby-facilities'),
    path('shortest-path/',get_shortest_path_distance, name= 'shortest-path'),
    path('recommendations/<int:prop_id>/',get_similar_recomendations, name= 'similar-properties'),
    path('k-cheapest/',get_top_cheepest, name= 'cheap-properties'),
    path('k-largest/',get_largest_sizes, name= 'large-properties'),
    
]