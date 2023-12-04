from django.urls import path
from django.urls import re_path
from . import views

urlpatterns = [
    path('places/<str:prompt>/<int:limit>', views.suggest_places, name='places'),
    path('trips/<str:origin>/<str:destination>/<str:origin_radius>/<str:dest_radius>/<int:timestamp>/<int:train_enabled>/<int:car_enabled>/<int:bike_enabled>', views.find_trips_simplified, name='trips'),
    path('trips/details/<str:origin>/<str:destination>/<str:origin_radius>/<str:dest_radius>/<int:timestamp>/<int:train_enabled>/<int:car_enabled>/<int:bike_enabled>', views.find_trips_complete, name='trips_details'),
    path('suggest/<str:prompt>/<str:lon>/<str:lat>', views.travel_suggestions, name='suggestions'),
    path('trace_path', views.trace_path, name='trace_path'),
    
    path('suggest/<str:prompt>', views.travel_suggestions, name='suggestions'),
    path('get_address/<str:lon>/<str:lat>', views.get_address, name='address'),
    path('get_coordinates/<str:address>', views.get_coordinates, name='coordinates'),
    path('car_infos/<str:lon1>/<str:lat1>/<str:lon2>/<str:lat2>', views.car_traject_infos, name='car'),
    path('bike_infos/<str:lon1>/<str:lat1>/<str:lon2>/<str:lat2>', views.bike_traject_infos, name='bike'),
    path('walk_infos/<str:lon1>/<str:lat1>/<str:lon2>/<str:lat2>', views.walk_traject_infos, name='walk'),
    #path("map/", views.get_path, name="communaute"),

    # Last one for the front-end
    re_path(r'^(?!/).*$', views.webpage, name='frontend'),
]
