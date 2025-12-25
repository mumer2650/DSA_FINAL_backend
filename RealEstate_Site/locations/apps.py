from django.apps import AppConfig


class LocationsConfig(AppConfig):
    name = 'locations'

    def ready(self):
        from .models import Location,Facility,Connection
        from .graphs import graph
        
        import sys
        if 'runserver' in sys.argv:
            locations = Location.objects.all()
            facilities = Facility.objects.all()
            connections = Connection.objects.all()
            
            for location in locations:
                graph.add_location(location)
                

            for conn in connections:
                graph.add_edge(conn.from_location.id, conn.to_location.id, conn.distance)
            
            