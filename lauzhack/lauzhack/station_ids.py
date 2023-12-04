import json

all_stations = None


def load_stations():
    print("Loading stations...")
    with open('lauzhack/resources/station_ids.json') as file:
        global all_stations
        all_stations = json.loads(file.read())


def station_id(station_name):
    if not all_stations:
        load_stations()
    return all_stations[station_name]
