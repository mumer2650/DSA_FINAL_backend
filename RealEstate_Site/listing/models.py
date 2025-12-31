from django.db import models
from users.models import User

class Property(models.Model):
    title = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    size = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    
    floors = models.IntegerField(default=1)
    kitchens = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    
    is_featured = models.BooleanField(default=False)
    
    image = models.ImageField(upload_to='properties/')
    location_id = models.ForeignKey('locations.Location', on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')