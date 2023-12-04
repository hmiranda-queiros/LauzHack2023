import json
import math
import re
import os

import requests
import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from . import generative_ai, geocoding, journey_selector, service_requests, transport


api_key = ""
try:
    with open(
        os.path.join(
            os.path.dirname(__file__), "..", "..", "keys", "journey-maps-api-sbb.txt"
        ),
        "r",
    ) as file:
        api_key = file.read()
except Exception as e:
    print(e)


@csrf_exempt
def suggest_places(request, prompt, limit):
    response = service_requests.get_request_places(prompt, limit)
    places = response.json()["places"]
    place_ids_and_names = list(
        map(
            lambda place: {
                "id": place["id"],
                "name": place["name"],
                "coordinates": place["centroid"]["coordinates"],
            },
            places,
        )
    )
    return JsonResponse(place_ids_and_names, safe=False)


@csrf_exempt
def create_timestamp(timing):
    return datetime.datetime.timestamp(datetime.datetime.fromisoformat(timing))


@csrf_exempt
def extract_duration(duration):
    match = re.match(r"PT(\d+H)?(\d+M)?", duration)
    hours = int(match.group(1)[:-1]) if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) if match.group(2) else 0
    return f"{hours:02d}{minutes:02d}"


def time_min(time):
    return int(time[:2]) * 60 + int(time[2:])


@csrf_exempt
def extract_coordinates(str_coordinates):
    return list(map(float, str_coordinates[1:-1].split(",")))


@csrf_exempt
def extract_coordinates(str_coordinates):
    return list(map(float, str_coordinates[1:-1].split(",")))


@csrf_exempt
def extract_datetime_from_timestamp(timestamp):
    from datetime import datetime

    date_time = datetime.fromtimestamp(timestamp)
    date = str(date_time.date())
    time = str(date_time.time())[:-3]
    return date, time


def extract_end_stop_point(leg, is_departure):
    foot = not leg.get("serviceJourney", None)
    stop_point = (
        leg["start" if is_departure else "end"]
        if foot
        else leg["serviceJourney"]["stopPoints"][0 if is_departure else -1]
    )
    place = stop_point["place"]
    timing = (
        stop_point["timeAimed"]
        if foot
        else stop_point["departure" if is_departure else "arrival"]["timeAimed"]
    )
    timestamp = create_timestamp(timing)
    return {
        "id": place.get("id", ""),
        "name": place.get("name", ""),
        "coordinates": place["centroid"]["coordinates"],
        "time": timestamp,
    }


@csrf_exempt
def find_trips_simplified(
    request,
    origin,
    destination,
    origin_radius,
    dest_radius,
    timestamp,
    train_enabled,
    car_enabled,
    bike_enabled,
):
    def extract_trips(trips):
        final_trips = []
        for trip in trips:
            legs = trip["legs"]
            departure = extract_end_stop_point(legs[0], True)
            arrival = extract_end_stop_point(legs[-1], False)
            final_trip = {"id": trip["id"], "departure": departure, "arrival": arrival}
            final_trips.append(final_trip)
        return final_trips

    (date, time) = extract_datetime_from_timestamp(timestamp)

    res = []
    departure = {"id": "", "name": origin, "coordinates": origin, "time": timestamp}
    if train_enabled:
        sbb_response = service_requests.post_request_trips(
            origin, destination, origin_radius, dest_radius, date, time
        )
        sbb_trips = sbb_response.json()["trips"]
        sbb_res = extract_trips(sbb_trips)
        res += sbb_res
        departure = sbb_res[0]["departure"]
    (dep_date, dep_time) = extract_datetime_from_timestamp(departure["time"])
    departure["time"] = f"{dep_date}T{dep_time}:00+01:00"

    (origin_lon, origin_lat) = extract_coordinates(origin)
    (destination_lon, destination_lat) = extract_coordinates(destination)

    if car_enabled:
        car_response = journey_selector.compute_all_additional_car_travels(
            origin_lon,
            origin_lat,
            destination_lon,
            destination_lat,
            10,
            departure,
            origin_radius,
            dest_radius,
            date,
            timestamp,
        )
        car_trips = car_response["trips"]
        car_res = extract_trips(car_trips)
        res += car_res

    if bike_enabled:
        bike_response = journey_selector.compute_all_additional_bike_travels(
            origin_lon,
            origin_lat,
            destination_lon,
            destination_lat,
            departure,
            origin_radius,
            dest_radius,
            date,
            timestamp,
            sbb_response,
        )
        bike_trips = bike_response["trips"]
        bike_res = extract_trips(bike_trips)
        res += bike_res

    return JsonResponse({"trips": res})


def extract_trips(trips):
        final_trips = []
        for trip in trips:
            legs = []
            for leg in trip["legs"]:
                locomotion_mode = leg["mode"]
                duration = leg.get("duration", "PT0H0M")
                distance = leg.get("distance", 0)
                co2g = leg.get("co2g", 0)
                cost = leg.get("cost", 0)
                if duration:
                    duration = extract_duration(duration)
                res_leg = {
                    "mode": locomotion_mode,
                    "duration": duration,
                    "co2g": co2g,
                    "cost": cost,
                    "distance": distance,
                }

                if locomotion_mode == "FOOT" or locomotion_mode == "TRANSFER":
                    res_leg["distance"] = time_min(duration) * 10 / 60

                    def extract_extremities(name):
                        place = leg[name]["place"]
                        res_leg[name] = {
                            "id": place["id"],
                            "name": place["name"],
                            "time": create_timestamp(leg[name]["timeAimed"]),
                            "coordinates": place["centroid"]["coordinates"],
                        }

                    extract_extremities("start")
                    extract_extremities("end")
                else:
                    if distance == 0:
                        res_leg["distance"] = time_min(duration) * 60 / 60
                    if co2g == 0:
                        res_leg["co2g"] = res_leg["distance"] * 5
                    if cost == 0:
                        res_leg["cost"] = res_leg["distance"] * 0.5
                    start = extract_end_stop_point(leg, True)
                    end = extract_end_stop_point(leg, False)
                    res_leg["start"] = start
                    res_leg["end"] = end

                legs.append(res_leg)
            final_trips.append({"id": trip["id"], "legs": legs})
        return final_trips

@csrf_exempt
def find_trips_complete(
    request,
    origin,
    destination,
    origin_radius,
    dest_radius,
    timestamp,
    train_enabled,
    car_enabled,
    bike_enabled,
):
    

    (date, time) = extract_datetime_from_timestamp(timestamp)

    res = []
    departure = {"id": "", "name": origin, "coordinates": origin, "time": timestamp}
    if train_enabled:
        sbb_response = service_requests.post_request_trips(
            origin, destination, origin_radius, dest_radius, date, time
        )
        sbb_trips = sbb_response.json()
        if "trips" in sbb_trips:
            sbb_trips = sbb_trips["trips"]
            sbb_res = extract_trips(sbb_trips)
            res += sbb_res

        departure = sbb_res[0]["legs"][0]["start"]
    (dep_date, dep_time) = extract_datetime_from_timestamp(departure["time"])
    departure["time"] = f"{dep_date}T{dep_time}:00+01:00"

    (origin_lon, origin_lat) = extract_coordinates(origin)
    (destination_lon, destination_lat) = extract_coordinates(destination)

    if car_enabled:
        car_response = journey_selector.compute_all_additional_car_travels(
            origin_lon,
            origin_lat,
            destination_lon,
            destination_lat,
            10,
            departure,
            origin_radius,
            dest_radius,
            date,
            timestamp,
        )
        car_trips = car_response
        if "trips" in car_trips:
            car_trips = car_trips["trips"]
            car_res = extract_trips(car_trips)
            res += car_res

    if bike_enabled:
        bike_response = journey_selector.compute_all_additional_bike_travels(
            origin_lon,
            origin_lat,
            destination_lon,
            destination_lat,
            departure,
            origin_radius,
            dest_radius,
            date,
            timestamp,
            sbb_response,
        )
        bike_trips = bike_response
        if "trips" in bike_trips:
            bike_trips = bike_trips["trips"]
            bike_res = extract_trips(bike_trips)
            res += bike_res

    return JsonResponse({"trips": res})


@csrf_exempt
def travel_suggestions(request, prompt, location=None):
    response = generative_ai.generate_response(prompt, location)
    return JsonResponse(response, safe=False)


@csrf_exempt
def travel_suggestions(request, prompt, lat=None, lon=None):
    response = generative_ai.generate_response(prompt, lat, lon)
    return JsonResponse(response, safe=False)


@csrf_exempt
def get_address(request, lat, lon):
    address = geocoding.geo_decode(lat, lon)
    return JsonResponse(address, safe=False)


@csrf_exempt
def get_coordinates(request, address):
    coordinates = geocoding.geo_encode(address)
    return JsonResponse(coordinates, safe=False)


@csrf_exempt
def car_traject_infos(request, lat1, lon1, lat2, lon2):
    traject_infos = transport.car_traject_infos(lat1, lon1, lat2, lon2)
    return JsonResponse(traject_infos, safe=False)


@csrf_exempt
def bike_traject_infos(request, lat1, lon1, lat2, lon2):
    traject_infos = transport.bike_traject_infos(lat1, lon1, lat2, lon2)
    return JsonResponse(traject_infos, safe=False)


@csrf_exempt
def walk_traject_infos(request, lat1, lon1, lat2, lon2):
    traject_infos = transport.walk_traject_infos(lat1, lon1, lat2, lon2)
    return JsonResponse(traject_infos, safe=False)


def webpage(request):
    return render(request, "index.html")

@csrf_exempt
def trace_path(request):
    trip = json.loads(request.body)
    legs = trip["legs"]
    result = []
    for leg in legs:
        path = dict()
        path["mode"] = leg["mode"]
        path["points"] = []
        if leg["mode"] == "BIKE":
            path["points"] = transport.bike_traject_infos(
                leg["start"]["coordinates"][1],
                leg["start"]["coordinates"][0],
                leg["end"]["coordinates"][1],
                leg["end"]["coordinates"][0],
            )["travel_coordinates"]
        elif leg["mode"] == "CAR":
            path["points"] = transport.car_traject_infos(
                leg["start"]["coordinates"][1],
                leg["start"]["coordinates"][0],
                leg["end"]["coordinates"][1],
                leg["end"]["coordinates"][0],
            )["travel_coordinates"]
        elif leg["mode"] == "FOOT":
            path["points"] = transport.walk_traject_infos(
                leg["start"]["coordinates"][1],
                leg["start"]["coordinates"][0],
                leg["end"]["coordinates"][1],
                leg["end"]["coordinates"][0],
            )["travel_coordinates"]
        else:
            pathh = "/v1/route"
            url = "https://journey-maps.api.sbb.ch" + pathh
            params = {
                "fromStationID": leg["start"]["id"],
                "toStationID": leg["end"]["id"],
                "api_key": api_key,
            }

            response = requests.get(url, params=params).json()
            path["points"] = response["features"][2]["geometry"]["coordinates"]

        path["points"] = [[min(a, b), max(a, b)] for a, b in path["points"]]
        result.append(path)

    return JsonResponse(result, safe=False)
