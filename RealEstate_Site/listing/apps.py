from django.apps import AppConfig

class ListingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'listing'

    def ready(self):
        from .models import Property
        from .trees import property_tree,size_tree
        
        # Check if we are running the actual server (prevents running during migrations)
        import sys
        if 'runserver' in sys.argv:
            print("Start: Loading Properties into AVL Tree...")
            all_properties = Property.objects.all()
            
            for p in all_properties:
                property_tree.insert(p)
                size_tree.insert(p)
                
            print(f"Success: Loaded {property_tree.size} properties into the AVL Tree.")