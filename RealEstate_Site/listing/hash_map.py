from .models import Favorite
from .stack import Stack

class FavoriteHashMap:
    def __init__(self, size=1000):
        self.size = size
        self._storage = [[] for _ in range(self.size)]

    def _hash(self, key):
        return hash(key) % self.size
    
    def is_favorite(self, user_id, property_id):
        fav_set = self.get_val(user_id)
        if fav_set is None:
            self.load_user_favorites(user_id)
            fav_set = self.get_val(user_id)
        
        return property_id in fav_set if fav_set else False

    def add_favorite(self, user_id, property_id):
        fav_set = self.get_val(user_id)
        if fav_set is None:
            self.load_user_favorites(user_id)
            fav_set = self.get_val(user_id)
        
        if fav_set is not None:
            fav_set.add(property_id)


    def set_val(self, user_id, fav_set):
        index = self._hash(user_id)
        bucket = self._storage[index]
        
        for i, (uid, fset) in enumerate(bucket):
            if uid == user_id:
                bucket[i] = (user_id, fav_set)
                return
        
        bucket.append((user_id, fav_set))

    def get_val(self, user_id):
        index = self._hash(user_id)
        bucket = self._storage[index]
        
        for uid, fset in bucket:
            if uid == user_id:
                return fset
        return None

            
    def load_user_favorites(self, user_id):
        fav_ids = Favorite.objects.filter(user_id=user_id).values_list('property_id', flat=True)
        self.set_val(user_id, set(fav_ids))

    def remove_favorite(self, user_id, property_id):
        fav_set = self.get_val(user_id)
        if fav_set:
            fav_set.discard(property_id)

    def get_all_for_user(self, user_id):
        fav_set = self.get_val(user_id)
        if fav_set is None:
            self.load_user_favorites(user_id)
            fav_set = self.get_val(user_id)
        
        return list(fav_set) if fav_set else []
    
class RecentlyViewedProperty:
    def __init__(self, size=1000):
        self.size = size
        self._storage = [[] for _ in range(self.size)]

    def _hash(self, key):
        return hash(key) % self.size

    def _get_stack(self, user_id):
        index = self._hash(user_id)
        bucket = self._storage[index]
        
        for uid, stack_obj in bucket:
            if uid == user_id:
                return stack_obj
        return None

    def add_view(self, user_id, property_id):
        user_stack = self._get_stack(user_id)
        
        if user_stack is None:
            user_stack = Stack(max_size=10)
            index = self._hash(user_id)
            self._storage[index].append((user_id, user_stack))
        
        user_stack.push(property_id)

    def get_history(self, user_id):
        user_stack = self._get_stack(user_id)
        if user_stack:
            return user_stack.get_all()
        return []
   
class SearchCache:
    def __init__(self):
        # Format { user_id : StackObject }
        self._storage = {}

    def add_query(self, user_id, query):
        if user_id not in self._storage:
            self._storage[user_id] = Stack(max_size=10)
        #ye jab search ki api bnao ge tab use karna
        self._storage[user_id].push(query)

    def get_search_history(self, user_id):
        user_stack = self._storage.get(user_id)
        if user_stack:
            return user_stack.get_all()
        return []

search_cache = SearchCache()
recent_view = RecentlyViewedProperty()
favorites_map = FavoriteHashMap()