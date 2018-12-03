from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from weather.models import Place, ZipCode

import csv


class Command (BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+')

    def handle(self, *args, **options):
        for f in options['files']:
            places = []
            for idx, row in enumerate(csv.reader(open(f, 'r'), dialect='excel-tab')):
                if idx == 0:
                    continue
                # Trim off the last word of the name (CDP, city, village, etc) unless it's only one word.
                parts = row[3].split()
                name = parts[0] if len(parts) == 1 else ' '.join(parts[:-1])
                point = Point(float(row[11]), float(row[10]), srid=4326)
                try:
                    zipcode = ZipCode.objects.get(bounds__covers=point)
                except ZipCode.DoesNotExist:
                    print(f'No zip code found for place on line {idx + 1}')
                    zipcode = None
                places.append(Place(
                    name=name,
                    state=row[0],
                    point=point,
                    zipcode=zipcode,
                ))
            Place.objects.all().delete()
            Place.objects.bulk_create(places)
