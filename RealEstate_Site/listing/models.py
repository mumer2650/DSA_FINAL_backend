from django.db import models

class Property(models.Model):
    title = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    area = models.TextField()
    size = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    image = models.ImageField(upload_to='media/properties/')
    location_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title