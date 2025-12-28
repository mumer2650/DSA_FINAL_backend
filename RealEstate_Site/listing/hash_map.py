from .models import Favorite
from .stack import Stack

class FavoriteHashMap:
    #Format user_id : int as a key and set of prop ids : int as val
    def __init__(self):
        self._storage = {} 

    def load_user_favorites(self, user_id):
        fav_ids = Favorite.objects.filter(user_id=user_id).values_list('property_id', flat=True)
        self._storage[user_id] = set(fav_ids)

    def is_favorite(self, user_id, property_id):
        if user_id not in self._storage:
            self.load_user_favorites(user_id)
        return property_id in self._storage.get(user_id, set())

    def add_favorite(self, user_id, property_id):
        if user_id not in self._storage:
            self.load_user_favorites(user_id)
        
        self._storage[user_id].add(property_id)
    
    def remove_favorite(self, user_id, property_id):
        if user_id in self._storage:
            self._storage[user_id].discard(property_id)
        
    def get_all_for_user(self, user_id):
        
        if user_id not in self._storage:
            self.load_user_favorites(user_id)
        
        return list(self._storage.get(user_id, set()))
    
class RecentlyViewedProperty:
    def __init__(self):
        # Format { user_id : StackObject }
        self._storage = {}

    def add_view(self, user_id, property_id):
        if user_id not in self._storage:
            self._storage[user_id] = Stack(max_size=10)
        
        self._storage[user_id].push(property_id)

    def get_history(self, user_id):
        user_stack = self._storage.get(user_id)
        if user_stack:
            return user_stack.get_all()
        return []

recent_view = RecentlyViewedProperty()
favorites_map = FavoriteHashMap()