from django.db import models
from users.models import User
from maps.models import MapNode  # Importing the map location we made earlier

class Category(models.Model):
    """
    Implements the Tree Data Structure for Categories.
    Example: Real Estate (Root) -> Residential (Child) -> Villa (Grandchild)
    """
    name = models.CharField(max_length=100)
    # 'self' means this model connects to itself (Parent-Child relationship)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.name

class Property(models.Model):
    # Basic Info
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)  # For BST Sorting
    area_sqft = models.IntegerField()  # For BST Sorting
    
    # Relationships
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    
    # The Connection to the Map (Graph Node)
    # Every house is physically located on a node in our custom map
    location_node = models.OneToOneField(MapNode, on_delete=models.SET_NULL, null=True, related_name='property_details')

    # Status
    listing_type = models.CharField(max_length=20, choices=[('SALE', 'For Sale'), ('RENT', 'For Rent')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    # for house images
    image = models.ImageField(upload_to='property_images/', blank=True, null=True)
# for this images to work we will need to install pillow (pip install pillow ) left for discussion in lab
    
    def __str__(self):
        return f"{self.title} - ${self.price}"