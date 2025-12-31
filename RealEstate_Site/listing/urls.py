from django.urls import path
from .views import add_property,get_properties, search_price_range,get_sorted_by_price,get_sorted_by_size, advanced_search,get_user_favorites,toggle_favorite,get_recent_list, bulk_add_properties, property_keyword_search, get_single_property_detail, get_featured_properties
urlpatterns = [
    path('create/', add_property, name='add_property'),
    path('search/',property_keyword_search, name="search"),
    path('create-bulk/', bulk_add_properties, name='add_properties'),
    path('get/', get_properties, name='get_properties'),
    path('get-featured/', get_featured_properties, name='get_featured_properties'),
    path('sorted/price/',get_sorted_by_price,name='sort_properties'),
    path('sorted/size/',get_sorted_by_size,name='sort_properties'),
    path('search/advanced/',advanced_search,name='search'),  #write this as query param ?min_price=100000&max_price=500000&min_size=1200&min_bedrooms=3
    path('favorites/', get_user_favorites, name='get_favorites'),
    path('favorites/toggle/', toggle_favorite, name='toggle_favorite'),
    path('view/<int:prop_id>/', get_single_property_detail, name='record_view'),
    path('recent/',get_recent_list, name='get_recent'),
    
]