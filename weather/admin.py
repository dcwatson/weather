from django.contrib import admin

from .models import Place, Station, Weather


@admin.register(Place)
class PlaceAdmin (admin.ModelAdmin):
    list_display = ('name', 'state', 'zipcode')
    list_filter = ('state',)
    ordering = ('state', 'name')


class WeatherInline (admin.TabularInline):
    model = Weather
    extra = 0


@admin.register(Station)
class StationAdmin (admin.ModelAdmin):
    list_display = ('code', 'name', 'state', 'last_fetched')
    list_filter = ('state',)
    ordering = ('state', 'code')
    inlines = (WeatherInline,)
