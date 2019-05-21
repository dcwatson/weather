from django.contrib.gis.db.models.functions import Distance
from django.http import JsonResponse

from .models import Place, Station, ZipCode

import re


state_re = re.compile(',? [a-z]{2}$', re.I)


def weather(request, query=None):
    # TODO: GeoIP lookup when no query?
    if query.isdigit():
        if len(query) != 5:
            return JsonResponse({'error': 'Zip codes must be 5 digits.'})
        try:
            zipcode = ZipCode.objects.get(code=query)
            # Find the closest Place to get a representative name for a zip code.
            place = Place.objects.annotate(distance=Distance('point', zipcode.center)).order_by('distance').first()
            # Find the closest weather reporting station.
            station = Station.objects.annotate(distance=Distance('point', zipcode.center)).order_by('distance').first()
        except ZipCode.DoesNotExist:
            return JsonResponse({'error': 'Could not find ZipCode matching query "{}".'.format(query)})
    else:
        try:
            station = Station.objects.get(code=query.upper())
            # Find the closest Place to the Station.
            place = Place.objects.annotate(distance=Distance('point', station.point)).order_by('distance').first()
        except Station.DoesNotExist:
            parts = query.replace(',', '').rsplit(None, 1)
            if len(parts) == 2 and len(parts[1]) == 2:
                try:
                    place = Place.objects.get(name__iexact=parts[0].strip(), state=parts[1].upper())
                except Place.DoesNotExist:
                    return JsonResponse({'error': 'Could not find Place matching query "{}".'.format(query)})
            else:
                try:
                    place = Place.objects.get(name__iexact=parts[0].strip())
                except Place.DoesNotExist:
                    return JsonResponse({'error': 'Could not find Place matching query "{}".'.format(query)})
            # Find the closest Station to the Place.
            station = Station.objects.annotate(distance=Distance('point', place.point)).order_by('distance').first()
    latest = station.latest()
    return JsonResponse({
        'ip': request.META['REMOTE_ADDR'],
        'query': query,
        'name': place.name,
        'state': place.state,
        'last_fetched': latest.date_fetched.isoformat(),
        'summary': str(latest),
        'current': latest.data,
    }, json_dumps_params={'indent': 2, 'sort_keys': True})
