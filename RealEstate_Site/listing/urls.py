from django.urls import path
from .views import add_property,get_properties, search_price_range,get_sorted_by_price,get_sorted_by_size, advanced_search


urlpatterns = [
    path('create/', add_property, name='add_property'),
    path('get/', get_properties, name='get_properties'),
    path('sorted/price',get_sorted_by_price,name='sort_properties'),
    path('sorted/size',get_sorted_by_size,name='sort_properties'),
    path('search/advanced/',advanced_search,name='search'),  #write this as query param ?min_price=100000&max_price=500000&min_size=1200&min_bedrooms=3
    
]