from django.contrib.gis.db.models.functions import Distance
from django.http import JsonResponse

from .models import Place, Station, ZipCode

import re


state_re = re.compile(',? [a-z]{2}$', re.I)


def weather(request, query=None):
    # TODO: GeoIP lookup when no query?
    if query.isdigit():
        zipcode = ZipCode.objects.get(code=query)
        # Find the closest Place to get a representative name for a zip code.
        place = Place.objects.annotate(distance=Distance('point', zipcode.center)).order_by('distance').first()
        # Find the closest weather reporting station.
        station = Station.objects.annotate(distance=Distance('point', zipcode.center)).order_by('distance').first()
        latest = station.latest()
        return JsonResponse({
            'query': query,
            'name': place.name,
            'state': place.state,
            'last_fetched': latest.date_fetched.isoformat(),
            'summary': str(latest),
            'current': latest.data,
        }, json_dumps_params={'indent': 2})
    return JsonResponse({'error': 'Could not parse query.'})
