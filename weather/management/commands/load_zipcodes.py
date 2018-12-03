from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand
import tqdm

from weather.models import ZipCode


class Command (BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+')

    def handle(self, *args, **options):
        for f in options['files']:
            ds = DataSource(f, encoding='utf-8')  # TODO: check encoding
            print(f'Processing {ds}')
            for layer in ds:
                zips = []
                for feature in tqdm.tqdm(layer, desc=layer.name):
                    geom = feature.geom
                    geom.transform('WGS84')
                    geos = geom.geos
                    zips.append(ZipCode(
                        code=feature.get('ZCTA5CE10'),
                        bounds=geos,
                        center=geos.centroid,
                    ))
            ZipCode.objects.bulk_create(zips)
