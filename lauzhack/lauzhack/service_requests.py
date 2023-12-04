import requests
import os

JOURNEY_SERVICE_URL = "https://journey-service-int.api.sbb.ch"
CAR_PARKS_URL = "https://data.sbb.ch/api/explore/v2.1/catalog/datasets/mobilitat/records"

api_key = ""
try:
    with open(
        os.path.join(
            os.path.dirname(__file__),"..","..", "keys", "microsoft_key.txt"
        ),
        "r",
    ) as file:
        api_key = file.read()
except Exception as e:
    print(e)

client_secret = ""
try:
    with open(
        os.path.join(
            os.path.dirname(__file__),"..","..", "keys", "microsoft_key.txt"
        ),
        "r",
    ) as file:
        client_secret = file.read()
except Exception as e:
    print(e)


def ask_for_token():
    token_url = "https://login.microsoftonline.com/2cda5d11-f0ac-46b3-967d-af1b2e1bd01a/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "scope": "api://c11fa6b1-edab-4554-a43d-8ab71b016325/.default",
        "client_id": "f132a280-1571-4137-86d7-201641098ce8",
        "client_secret": client_secret,
    }
    token_response = requests.post(token_url, data=token_data)
    return token_response.json()["access_token"]


def get_request_places(nameMatch, limit):
    # (Use places API instead of stop-places one because it gives more relevant results)
    url = JOURNEY_SERVICE_URL + f"/v3/places?nameMatch={nameMatch}&limit={limit}&type=ALL"
    token = ask_for_token()
    headers = {
        'Authorization': f"Bearer {token}",
    }
    response = requests.get(url=url, headers=headers)
    return response


def post_request_trips(origin, destination, origin_radius, dest_radius, date, time):
    url = JOURNEY_SERVICE_URL + f"/v3/trips/by-origin-destination"
    token = ask_for_token()
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    }
    body = {
        "origin": origin,
        "destination": destination,
        "originRadius": origin_radius,
        "destinationRadius": dest_radius,
        "date": date,
        "time": time
    }
    response = requests.post(url=url, headers=headers, json=body)
    return response

def modif_post(request, from_id, to_id):
    path = "/v1/route"
    url = "https://journey-maps.api.sbb.ch" + path
    params = {"fromStationID": from_id, "toStationID": to_id, "api_key": api_key}

    response = requests.get(url, params=params)
    return response.json()

def get_request_car_parks():
    url = CAR_PARKS_URL
    params = {
        "limit": -1,
    }
    response = requests.get(url, params=params)
    return response
