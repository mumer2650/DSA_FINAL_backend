from django.contrib import admin
from .models import Location, Facility, Connection

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('from_location', 'to_location', 'distance')