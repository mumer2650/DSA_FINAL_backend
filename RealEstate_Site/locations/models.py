from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100)
    
    
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