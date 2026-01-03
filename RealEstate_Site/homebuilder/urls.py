
from django.urls import path
from .views import GenerateLayoutView, UserLayoutsView, LayoutDetailView

app_name = 'homebuilder'

urlpatterns = [
    path('generate/', GenerateLayoutView.as_view(), name='generate_layout'),
    path('my-layouts/', UserLayoutsView.as_view(), name='user_layouts'),
    path('layout/<int:layout_id>/', LayoutDetailView.as_view(), name='layout_detail'),
]
