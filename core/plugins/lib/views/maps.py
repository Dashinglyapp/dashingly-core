from core.plugins.lib.views.base import View

class MapDescriptor(object):
    def __init__(self, lon, lat, date):
        self.lon = lon
        self.lat = lat
        self.date = date

class MapView(View):
    name = None
    description = None
    tags = ["view", "map"]

    def get_map_points(self, data):
        """
        Should be a list of MapDescriptors.
        """

        raise NotImplementedError()

    def to_json(self, data):
        map_points = self.get_map_points(data)
        map_list = []
        for m in map_points:
            map_list.append(dict(
                lat=m.lat,
                lon=m.lon,
                date=m.date
            ))
        return {
            'points': map_list
            }

class SimpleMapView(MapView):
    model = None
    lat_field = "latitude"
    lon_field = "longitude"
    date_field = "date"

    def get_map_points(self, data):
        start = data.get('start', None)
        end = data.get('end', None)
        data = self.manager.query_class_range("date", self.model, start=start, end=end)

        map_points = []
        for d in data:
            map_points.append(
                MapDescriptor(
                    getattr(d, self.lat_field, None),
                    getattr(d, self.lon_field, None),
                    getattr(d, self.date_field, None)
                )
            )
        return map_points

