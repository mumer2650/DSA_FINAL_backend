from django.contrib import admin
from .models import Location, Facility, Connection
import locations.signals

@admin.action(description='Delete selected locations and sync DSA structures')
def delete_with_dsa_sync(modeladmin, request, queryset):
    # We iterate through the selected locations
    count = 0
    for location in queryset:
        try:

            location.delete()
            count += 1
        except Exception as e:
            modeladmin.message_user(request, f"Error deleting ID {location.id}: {e}")

    modeladmin.message_user(request, f"Successfully deleted {count} locations and synced DSA heaps/trees.")

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('from_location', 'to_location', 'distance')
    
class FacilityInline(admin.TabularInline):
    model = Facility
    extra = 1  
    min_num = 1

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_type', 'latitude', 'longitude')
    
    exclude = ('location_type',) 

    inlines = [FacilityInline]

    def save_model(self, request, obj, form, change):
        obj.location_type = 'facility'
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj)
