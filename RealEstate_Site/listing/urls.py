from django.urls import path
from .views import add_property,get_properties


urlpatterns = [
    path('create/', add_property, name='add_property'),
    path('/', get_properties, name='get_properties'),
]