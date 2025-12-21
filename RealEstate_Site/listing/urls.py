from django.urls import path
from .views import add_property,get_properties, search_price_range,get_sorted_by_price,get_sorted_by_size


urlpatterns = [
    path('create/', add_property, name='add_property'),
    path('get/', get_properties, name='get_properties'),
    path('search/', search_price_range, name='search_price_range'),
    path('sorted/price',get_sorted_by_price,name='sort_properties'),
    path('sorted/size',get_sorted_by_size,name='sort_properties'),
]