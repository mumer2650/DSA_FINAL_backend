from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Favorite
from .hash_map import favorites_map

@receiver(post_save, sender=Favorite)
def update_hash_map_on_save(sender, instance, created, **kwargs):
    if created:
        favorites_map.add_favorite(instance.user_id, instance.property_id)

@receiver(post_delete, sender=Favorite)
def update_hash_map_on_delete(sender, instance, **kwargs):
    favorites_map.remove_favorite(instance.user_id, instance.property_id)