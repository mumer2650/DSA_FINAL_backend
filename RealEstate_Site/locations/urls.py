from django.urls import path
from .views import get_nearby_facilities,get_shortest_path_distance


urlpatterns = [
    path('nearby/<int:prop_id>/', get_nearby_facilities, name='nearby-facilities'),
    path('shortest-path/',get_shortest_path_distance, name= 'shortest-path')
    
]