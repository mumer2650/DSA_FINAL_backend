from django.db import models
from users.models import User

class LayoutRequest(models.Model):
    """
    Stores the user's constraints for the Home Builder.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="My Dream House")
    
    # Constraints (Input for the BSP Algorithm)
    plot_width = models.IntegerField(help_text="Width in feet")
    plot_length = models.IntegerField(help_text="Length in feet")
    min_room_size = models.IntegerField(default=100, help_text="Minimum sqft for a room")
    complexity_level = models.IntegerField(default=4, help_text="Recursion depth for BSP")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.plot_width}x{self.plot_length})"

class GeneratedBlueprint(models.Model):
    """
    Stores the OUTPUT of your BSP Algorithm.
    """
    request = models.OneToOneField(LayoutRequest, on_delete=models.CASCADE, related_name='blueprint')
    
    # We store the tree structure as JSON. 
    # The Frontend (React) will read this JSON to draw the rectangles on the Canvas.
    structure_json = models.JSONField(help_text="The JSON representation of the BSP Tree layout")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blueprint for {self.request.name}"