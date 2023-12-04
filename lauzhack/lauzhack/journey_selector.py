from math import asin, cos, radians, sin, sqrt

from . import service_requests, transport


def extract_datetime_from_timestamp(timestamp):
    from datetime import datetime

    date_time = datetime.fromtimestamp(timestamp)
    date = str(date_time.date())
    time = str(date_time.time())[:-3]
    return date, time


def get_available_car_parks_in_a_circle(data, center_lon, center_lat, radius):
    car_parks = data["results"]
    valid_car_parks = []
    for car_park in car_parks:
        if car_park["parkrail_anzahl"] == None or car_park["parkrail_anzahl"] <= 0:
            continue
        lon = car_park["geopos"]["lon"]
        lat = car_park["geopos"]["lat"]
        if not lat or not lon:
            continue
        distance = haversine_distance(lon, lat, center_lon, center_lat)
        if distance <= radius:
            valid_car_park = {}
            valid_car_park["park_day_price"] = car_park["parkrail_preis_tag"]
            valid_car_park["lon"] = lon
            valid_car_park["lat"] = lat
            valid_car_park["rental_bike_available"] = (
                True
                if car_park["mietvelo_anzahl"] != None
                and car_park["mietvelo_anzahl"] > 0
                else False
            )
            valid_car_parks.append(valid_car_park)

    return valid_car_parks


def get_available_car_parks_in_double_half_circle(
    data, center_lon_1, center_lat_1, center_lon_2, center_lat_2
):
    car_parks = data["results"]
    radius = haversine_distance(center_lon_1, center_lat_1, center_lon_2, center_lat_2)
    valid_car_parks = []
    for car_park in car_parks:
        if car_park["parkrail_anzahl"] == None or car_park["parkrail_anzahl"] <= 0:
            continue
        lon = car_park["geopos"]["lon"]
        lat = car_park["geopos"]["lat"]
        if not lat or not lon:
            continue
        distance_1 = haversine_distance(lon, lat, center_lon_1, center_lat_1)
        distance_2 = haversine_distance(lon, lat, center_lon_2, center_lat_2)
        if distance_1 <= radius and distance_2 <= radius:
            valid_car_park = {}
            valid_car_park["park_day_price"] = car_park["parkrail_preis_tag"]
            valid_car_park["lon"] = lon
            valid_car_park["lat"] = lat
            valid_car_park["rental_bike_available"] = (
                True
                if car_park["mietvelo_anzahl"] != None
                and car_park["mietvelo_anzahl"] > 0
                else False
            )
            valid_car_parks.append(valid_car_park)

    return valid_car_parks


def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers.
    return c * r


def get_optimal_available_car_parks(
    origin_lon, origin_lat, destination_lon, destination_lat, radius_small_circle
):
    data = service_requests.get_request_car_parks().json()

    available_car_parks_in_small_circle = get_available_car_parks_in_a_circle(
        data, origin_lon, origin_lat, radius_small_circle
    )
    available_car_parks_in_double_half_circle = (
        get_available_car_parks_in_double_half_circle(
            data, origin_lon, origin_lat, destination_lon, destination_lat
        )
    )

    available_car_parks_in_small_circle = {
        frozenset(d.items()) for d in available_car_parks_in_small_circle
    }
    available_car_parks_in_double_half_circle = {
        frozenset(d.items()) for d in available_car_parks_in_double_half_circle
    }

    optimal_available_car_parkarks = available_car_parks_in_small_circle.union(
        available_car_parks_in_double_half_circle
    )
    optimal_available_car_parkarks = [dict(d) for d in optimal_available_car_parkarks]

    return optimal_available_car_parkarks


def compute_all_additional_car_travels(
    origin_lon,
    origin_lat,
    destination_lon,
    destination_lat,
    radius_small_circle,
    start_stop_point,
    origin_radius,
    dest_radius,
    date,
    timestamp,
):
    optimal_available_car_parks = get_optimal_available_car_parks(
        origin_lon, origin_lat, destination_lon, destination_lat, radius_small_circle
    )

    all_possible_car_travels = {"trips": []}

    for car_park in optimal_available_car_parks:
        origin = f"[{car_park['lon']},{car_park['lat']}]"
        destination = f"[{destination_lon}, {destination_lat}]"
        car_traject_infos = transport.car_traject_infos(
            origin_lat, origin_lon, car_park["lat"], car_park["lon"]
        )
        response = service_requests.post_request_trips(
            origin,
            destination,
            origin_radius,
            dest_radius,
            date,
            extract_datetime_from_timestamp(timestamp + car_traject_infos["time"])[1],
        )
        trips = response.json()["trips"]

        car_leg = dict()
        car_leg["mode"] = "CAR"
        car_leg["duration"] = car_traject_infos["duration"]
        car_leg["cost"] = car_traject_infos["cost"]
        car_leg["co2g"] = car_traject_infos["co2g"]
        car_leg["distance"] = car_traject_infos["distance"]
        car_leg["serviceJourney"] = dict()
        car_leg["serviceJourney"]["stopPoints"] = list()
        car_leg["serviceJourney"]["stopPoints"].append(
            {
                "place": {
                    "type": "StopPlace",
                    "id": start_stop_point["id"],
                    "name": start_stop_point["name"],
                    "centroid": {
                        "coordinates": start_stop_point["coordinates"],
                    },
                },
                "departure": {
                    "timeAimed": start_stop_point["time"],
                },
            }
        )
        car_leg["serviceJourney"]["stopPoints"].append(
            {
                "place": {
                    "type": "StopPlace",
                    "name": "Car park",
                    "centroid": {
                        "coordinates": [car_park["lon"], car_park["lat"]],
                    },
                },
                "arrival": {
                    "timeAimed": transport.add_date(
                        start_stop_point["time"], car_traject_infos["time"]
                    ),
                },
            }
        )

        for trip in trips:
            legs = trip["legs"]
            legs.insert(0, car_leg)

        all_possible_car_travels["trips"].extend(trips)

    return all_possible_car_travels


def compute_all_additional_bike_travels(
    origin_lon,
    origin_lat,
    destination_lon,
    destination_lat,
    start_stop_point,
    origin_radius,
    dest_radius,
    date,
    timestamp,
    response,
):
    all_possible_bike_travels = {"trips": []}

    trips = response.json()["trips"]

    for trip in trips:
        if len(trip["legs"]) == 0:
            continue

        if trip["legs"][0]["mode"] == "FOOT":
            while trip["legs"][0]["mode"] != "TRAIN":
                trip["legs"].pop(0)
                if len(trip["legs"]) == 0:
                    break
        else:
            continue

        if len(trip["legs"]) == 0:
            continue

        train_leg = trip["legs"][0]
        train_leg_coordinates = train_leg["serviceJourney"]["stopPoints"][0]["place"][
            "centroid"
        ]["coordinates"]
        bike_traject_infos = transport.bike_traject_infos(
            origin_lat,
            origin_lon,
            train_leg_coordinates[1],
            train_leg_coordinates[0],
        )
        train_leg["serviceJourney"]["stopPoints"][0]["arrival"] = {
            "timeAimed": transport.add_date(
                start_stop_point["time"], bike_traject_infos["time"]
            )
        }
        train_leg["serviceJourney"]["stopPoints"][0].pop("departure")

        bike_leg = dict()
        bike_leg["mode"] = "BIKE"
        bike_leg["duration"] = bike_traject_infos["duration"]
        bike_leg["cost"] = bike_traject_infos["cost"]
        bike_leg["co2g"] = bike_traject_infos["co2g"]
        bike_leg["distance"] = bike_traject_infos["distance"]
        bike_leg["serviceJourney"] = dict()
        bike_leg["serviceJourney"]["stopPoints"] = list()
        bike_leg["serviceJourney"]["stopPoints"].append(
            {
                "place": {
                    "type": "StopPlace",
                    "id": start_stop_point["id"],
                    "name": start_stop_point["name"],
                    "centroid": {
                        "coordinates": start_stop_point["coordinates"],
                    },
                },
                "departure": {
                    "timeAimed": start_stop_point["time"],
                },
            }
        )
        bike_leg["serviceJourney"]["stopPoints"].append(
            train_leg["serviceJourney"]["stopPoints"][0]
        )

        response_train = service_requests.post_request_trips(
            f"[{train_leg_coordinates[0]},{train_leg_coordinates[1]}]",
            f"[{destination_lon}, {destination_lat}]",
            origin_radius,
            dest_radius,
            date,
            extract_datetime_from_timestamp(timestamp + bike_traject_infos["time"])[1],
        )

        trips_train = response_train.json()["trips"]

        for tripp in trips_train:
            legs = tripp["legs"]
            legs.insert(0, bike_leg)

        all_possible_bike_travels["trips"].extend(trips_train)

    return all_possible_bike_travels


# http://127.0.0.1:8000/trips/details/[6.5601536,46.514176]/[6.211753,46.401823]/1000/1000/1701566527
# a = compute_all_additional_car_travels(
#     6.5601536,
#     46.514176,
#     6.211753,
#     46.401823,
#     1000,
#     {
#         "id": "8503000",
#         "name": "Lausanne",
#         "coordinates": [6.632273, 46.519653],
#         "time": "2023-04-18T15:11:00+02:00",
#     },
#     "1000",
#     "1000",
#     "2023-04-18",
#     1701566527,
# )
# print(a)
