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
    
    image = models.ImageField(upload_to='properties/', null=True, blank=True)
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
        

class PropertyRequest(models.Model):
    TYPE_CHOICES = (
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    
    sell_prop = models.ForeignKey('SellPropertyDetail', on_delete=models.CASCADE, null=True, blank=True)
    
    request_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        title = self.property.title if self.property else self.sell_prop.title
        return f"{self.user.username} - {title} ({self.request_type})"
    
class SellPropertyDetail(models.Model):

    title = models.CharField(max_length=255)
    location_name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
    
    def __str__(self):
        return f"Sell Detail for Request #{self.request.id}: {self.title}"