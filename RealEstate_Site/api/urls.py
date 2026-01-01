
from django.urls import path , include


urlpatterns = [
    path('', include('users.urls')),
    path('properties/', include('listing.urls')),
    path('location/',include('locations.urls')),
    path('homebuilder/',include('homebuilder.urls')),
]
