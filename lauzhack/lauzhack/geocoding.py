import time
import requests


def geo_encode(address,try_count=0):
    """ Encode an address into a lat/long pair. """
    
    # Use this url to query https://geocode.maps.co/search?q={address}
    print(f"GeoCoding {address}")

    request = requests.get(f"https://geocode.maps.co/search?q={address}")
    if request.status_code == 429:
        print("ERROR: Geocoding failed")
        if try_count > 3:
            return None
        time.sleep(1)
        return geo_encode(address,try_count+1)
    response = request.json()

    return {
        "lat": response[0]["lat"],
        "lon": response[0]["lon"],
    }


def geo_decode(lat, lon):
    """ Decode a lat/long pair into an address. """
    #https://geocode.maps.co/reverse?lat=46.5218269&lon=6.6327025
    url = f"https://geocode.maps.co/reverse?lat={lat}&lon={lon}"
    request = requests.get(url)
    if request.status_code == 429:
        print("ERROR: Geocoding failed")
        time.sleep(1)
        return geo_decode(lat, lon)
    
    response = request.json()

    return response['display_name']

