from django.db import models
from locations.models import Connection

class Property(models.Model):
    title = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    area = models.TextField()
    size = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    image = models.ImageField(upload_to='properties/')
    location_id = models.ForeignKey('locations.Location', on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    