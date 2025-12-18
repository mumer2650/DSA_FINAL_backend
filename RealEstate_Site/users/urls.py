from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import register_user, user_profile, logout_user


urlpatterns = [
    path('auth/register/', register_user, name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'), 
    path('auth/logout/', logout_user, name='logout'),
    path('auth/profile/', user_profile, name='profile'),
]