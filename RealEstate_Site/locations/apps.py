from django.apps import AppConfig


class LocationsConfig(AppConfig):
    name = 'locations'

    def ready(self):
        from .models import Location,Facility,Connection
        from .graphs import graph
        
        import sys
        if 'runserver' in sys.argv:
            locations = Location.objects.all()
            connections = Connection.objects.all()
            
            for location in locations:
                graph.add_location(location)
            
            for conn in connections:
                graph.add_edge(conn.from_location.id, conn.to_location.id, conn.distance)
                graph.add_edge(conn.to_location.id,conn.from_location.id, conn.distance)
                
            #facilities_locations = Location.objects.filter(location_type='facility')
            
            # for fac_loc in facilities_locations:
            #     if not Connection.objects.filter(from_location=fac_loc).exists():
            #         graph.auto_connect_location(fac_loc, radius_km=5.0)
            
            