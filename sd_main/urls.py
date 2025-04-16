from django.urls import path
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("vehicles/", views.vehicles, name="vehicles"),
    path("drivers/", views.drivers, name="drivers"),
]
