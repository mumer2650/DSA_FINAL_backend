from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class HomeLayout(models.Model):
    """
    Main entity representing one generated house layout.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    length = models.FloatField()  # Total length of the house
    width = models.FloatField()   # Total width of the house
    floors = models.IntegerField()  # Number of floors (1-3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Home Layout by {self.user.username} - {self.floors} floors"

    class Meta:
        ordering = ['-created_at']


class Room(models.Model):
    """
    Generic Room class representing individual rooms in a house layout.
    """
    ROOM_TYPES = [
        ('BEDROOM', 'Bedroom'),
        ('KITCHEN', 'Kitchen'),
        ('BATH', 'Bathroom'),
        ('LIVING', 'Living Room'),
        ('HALL', 'Hallway'),
        ('STAIR', 'Stairway'),
    ]

    home = models.ForeignKey(HomeLayout, related_name='rooms', on_delete=models.CASCADE)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    floor = models.IntegerField()  # Floor number (0-based)
    x = models.FloatField()  # X position (percentage-based)
    y = models.FloatField()  # Y position (percentage-based)
    width = models.FloatField()  # Width (percentage-based)
    height = models.FloatField()  # Height (percentage-based)

    def __str__(self):
        return f"{self.room_type} on floor {self.floor} - {self.home}"

    class Meta:
        ordering = ['floor', 'room_type']
