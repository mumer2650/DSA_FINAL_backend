from django.db import models
from .utilis import calculate_haversine

class Location(models.Model):
    LOCATION_TYPES = [
        ('property', 'Property'),
        ('facility', 'Facility')
    ]
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField()  
    longitude = models.FloatField()
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, default='property')
    
    def __str__(self):
        return self.name
    
    
class Facility(models.Model):
    FACILITY_TYPES = [
        ('school', 'School'),
        ('hospital', 'Hospital'),
        ('park', 'Park'),
        ('mosque', 'Mosque'),
        ('airport', 'Airport'),
        ('police_station', 'Police Station'),
    ]
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='facilities')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=FACILITY_TYPES)
    

class Connection(models.Model):
    from_location = models.ForeignKey(Location, related_name='connections_from', on_delete=models.CASCADE)
    to_location = models.ForeignKey(Location, related_name='connections_to', on_delete=models.CASCADE)
    
    distance = models.FloatField(editable=False) 

    class Meta:
        unique_together = ('from_location', 'to_location')

    def save(self, *args, **kwargs):
        self.distance = calculate_haversine(
            self.from_location.latitude, self.from_location.longitude,
            self.to_location.latitude, self.to_location.longitude
        )
        super().save(*args, **kwargs)