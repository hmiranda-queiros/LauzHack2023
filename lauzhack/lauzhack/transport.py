import datetime
import re
import requests
import os
import polyline

mapbox_access_token = None


def init_token():
    try:
        with open(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "keys", "mapbox_key.txt"
            ),
            "r",
        ) as file:
            global mapbox_access_token
            mapbox_access_token = file.read()
    except Exception as e:
        print(e)


car_cost_per_km = 0.74
car_co2g_per_km = 114.1
bike_co2g_per_km = 8


def car_traject_infos(lat1, lon1, lat2, lon2):
    # https://api.mapbox.com/directions/v5/{profile}/{coordinates}

    if not mapbox_access_token:
        init_token()

    request = requests.get(
        f"https://api.mapbox.com/directions/v5/mapbox/driving/{lon1},{lat1};{lon2},{lat2}?access_token={mapbox_access_token}"
    )
    response = request.json()
    result = {}
    result["distance"] = response["routes"][0]["distance"] / 1000
    result["travel_coordinates"] = polyline.decode(response["routes"][0]["geometry"])
    result["cost"] = result["distance"] * car_cost_per_km
    result["co2g"] = result["distance"] * car_co2g_per_km
    result["duration"] = format_duration(response["routes"][0]["duration"])
    result["time"] = response["routes"][0]["duration"]

    return result



def bike_traject_infos(lat1, lon1, lat2, lon2):
    # https://api.mapbox.com/directions/v5/{profile}/{coordinates}

    if not mapbox_access_token:
        init_token()
    request = requests.get(
        f"https://api.mapbox.com/directions/v5/mapbox/cycling/{lon1},{lat1};{lon2},{lat2}?access_token={mapbox_access_token}"
    )
    response = request.json()
    result = {}
    result["distance"] = response["routes"][0]["distance"] / 1000
    result["travel_coordinates"] = polyline.decode(response["routes"][0]["geometry"])
    result["cost"] = 0
    result["co2g"] = result['distance'] * bike_co2g_per_km
    result["duration"] = format_duration(response["routes"][0]["duration"])
    result["time"] = response["routes"][0]["duration"]

    return result

def walk_traject_infos(lat1, lon1, lat2, lon2):
    # https://api.mapbox.com/directions/v5/{profile}/{coordinates}

    if not mapbox_access_token:
        init_token()
    request = requests.get(
        f"https://api.mapbox.com/directions/v5/mapbox/walking/{lon1},{lat1};{lon2},{lat2}?access_token={mapbox_access_token}"
    )
    response = request.json()
    result = {}
    result["distance"] = response["routes"][0]["distance"] / 1000
    result["travel_coordinates"] = polyline.decode(response["routes"][0]["geometry"])
    result["cost"] = 0
    result["co2g"] = 0
    result["duration"] = format_duration(response["routes"][0]["duration"])
    result["time"] = response["routes"][0]["duration"]

    return result


def format_duration(duration):
    time = "PT"
    if duration > 3600:
        time += str(int(duration // 3600)) + "H"
    if duration % 3600 > 60:
        time += str(int(duration % 3600 // 60)) + "M"
    return time if time != "PT" else "PT0M"


def add_date(date: str, duration: str):
    # 2023-04-18T15:04:00+02:00
    d = datetime.datetime.fromisoformat(date)
    d += datetime.timedelta(seconds=int(duration))
    return d.isoformat()
