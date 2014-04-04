from core.plugins.lib.views.base import View
from core.plugins.lib.views.maps import SimpleMapView
from plugins.foursquare.models import Checkins

class CheckinMap(SimpleMapView):
    name = 'foursquare_checkins'
    description = 'Checkins in foursquare.'
    model = Checkins
    lat_field = "latitude"
    lon_field = "longitude"
    date_field = "date"