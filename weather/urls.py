from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [
    path('weather/<query>/', views.weather, name='weather'),
    path('admin/', admin.site.urls),
]
