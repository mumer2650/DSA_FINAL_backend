from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class HomeLayout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    length = models.FloatField()
    width = models.FloatField()
    floors = models.IntegerField()
    request_payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Home Layout by {self.user.username} - {self.floors} floors"

    class Meta:
        ordering = ['-created_at']

class Room(models.Model):
    ROOM_TYPES = [
        ('ATTACHED_BED_BATH', 'Attached Bedroom + Bath'),
        ('KITCHEN', 'Kitchen'),
        ('LIVING', 'Living Room'),
        ('KITCHEN_LIVING_DINING_HUB', 'Kitchen Living Dining Hub'),
        ('HALL', 'Hallway'),
        ('STAIR', 'Stairway'),
        ('STUDYROOM', 'Study Room'),
        ('STORAGE', 'Storage'),
    ]

    home = models.ForeignKey(HomeLayout, related_name='rooms', on_delete=models.CASCADE)
    room_type = models.CharField(max_length=30, choices=ROOM_TYPES)
    floor = models.IntegerField()
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    def __str__(self):
        return f"{self.room_type} on floor {self.floor} - {self.home}"

    class Meta:
        ordering = ['floor', 'room_type']
