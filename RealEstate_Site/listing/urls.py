from django.urls import path
from . import views
urlpatterns = [
    path('create/', views.add_property, name='add_property'),
    path('search/',views.property_keyword_search, name="search"),
    path('create-bulk/', views.bulk_add_properties, name='add_properties'),
    path('get/', views.get_properties, name='get_properties'),
    path('get-featured/', views.get_featured_properties, name='get_featured_views.properties'),
    path('sorted/price/',views.get_sorted_by_price,name='sort_properties'),
    path('sorted/size/',views.get_sorted_by_size,name='sort_properties'),
    path('search/advanced/',views.advanced_search,name='search'),  #write this as query param ?min_price=100000&max_price=500000&min_size=1200&min_bedrooms=3
    path('favorites/', views.get_user_favorites, name='get_favorites'),
    path('favorites/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('view/<int:prop_id>/', views.get_single_property_detail, name='record_view'),
    path('recent/',views.get_recent_list, name='get_recent'),
    path('all-requests/', views.get_all_requests, name='get_all_requests'),
    path('submit-buy-request/', views.create_property_request, name='submit_request'),
    path('submit-sell-request/', views.submit_sell_request, name='submit_sell_request'),
    path('manage-request/<int:request_id>/', views.manage_property_request, name='manage_request'),
]