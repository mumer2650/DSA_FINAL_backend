from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Location
from .utilis import calculate_haversine

@receiver(post_save, sender=Location)
def connect_to_nearest_waypoint(sender, instance, created, **kwargs):
    # Only run when a NEW location is created and it's NOT a waypoint itself
    if created and instance.location_type in ['property', 'facility']:
        
        waypoints = Location.objects.filter(location_type='way_point')
        
        nearest_waypoint = None
        min_distance = float('inf')

        for wp in waypoints:
            dist = calculate_haversine(
                instance.latitude, instance.longitude,
                wp.latitude, wp.longitude
            )
            
            if dist < min_distance:
                min_distance = dist
                nearest_waypoint = wp

        if nearest_waypoint:
            from .models import Connection 
            
            Connection.objects.get_or_create(
                from_location=instance,
                to_location=nearest_waypoint
            )
