from django.contrib.gis.db.models.fields import GeometryField, PointField
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
import drill
import requests

import datetime


class ZipCode (models.Model):
    code = models.CharField(max_length=5, unique=True)
    bounds = GeometryField(geography=True)
    center = PointField()

    def __str__(self):
        return self.code


class Place (models.Model):
    name = models.CharField(max_length=200)
    state = models.CharField(max_length=2)
    point = PointField()
    zipcode = models.ForeignKey(ZipCode, related_name='places', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Station (models.Model):
    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=200)
    state = models.CharField(max_length=2)
    point = PointField()
    xml_url = models.CharField(max_length=200)
    last_fetched = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def fetch(self):
        r = requests.get(self.xml_url, timeout=5)
        doc = drill.parse(r.text)
        self.last_fetched = timezone.now()
        self.save(update_fields=('last_fetched',))
        return self.weather.create(data=doc.json(), date_fetched=self.last_fetched)

    def latest(self):
        if self.last_fetched and (timezone.now() - self.last_fetched) < datetime.timedelta(minutes=15):
            return self.weather.latest('date_fetched')
        else:
            return self.fetch()


class Weather (models.Model):
    station = models.ForeignKey(Station, related_name='weather', on_delete=models.CASCADE)
    data = JSONField()
    date_fetched = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '{} and {} ({}% humidity)'.format(self.data['temp_f'], self.data['weather'], self.data['relative_humidity'])
