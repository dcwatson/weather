from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
import drill
import requests

from weather.models import Station


class Command (BaseCommand):

    def handle(self, *args, **options):
        r = requests.get('https://w1.weather.gov/xml/current_obs/index.xml')
        doc = drill.parse(r.text)
        stations = []
        for s in doc.iter('station'):
            point = Point(float(s.longitude.data), float(s.latitude.data), srid=4326)
            stations.append(Station(
                code=s.station_id.data,
                name=s.station_name.data,
                state=s.state.data,
                point=point,
                xml_url=s.xml_url.data,
            ))
        Station.objects.bulk_create(stations)
