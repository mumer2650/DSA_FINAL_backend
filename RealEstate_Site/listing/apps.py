from django.apps import AppConfig

class ListingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'listing'

    def ready(self):
        from .models import Property
        from .trees import property_tree,size_tree
        from .heap import cheap_heap,size_heap
    
        import sys
        if 'runserver' in sys.argv:
            print("Start: Loading Properties into AVL Tree...")
            all_properties = Property.objects.all()
            
            for p in all_properties:
                property_tree.insert(p)
                size_tree.insert(p)
                cheap_heap.insert(p)
                size_heap.insert(p)
                
            print(f"Success: Loaded {property_tree.size} properties into the AVL Tree.")