
import requests
import os
import polyline

mapbox_access_token = ''
try:
    with open(os.path.join(os.path.dirname(__file__),"..","..","keys", 'mapbox_key.txt'), 'r') as file:
        mapbox_access_token = file.read()
except Exception as e:
        print(e)

car_cost_per_km = 0.74
car_co2g_per_km = 114.1

def car_traject_infos(lat1, lon1, lat2, lon2):
    #https://api.mapbox.com/directions/v5/{profile}/{coordinates}
    

    request = requests.get(f"https://api.mapbox.com/directions/v5/mapbox/driving/{lon1},{lat1};{lon2},{lat2}?access_token={mapbox_access_token}")
    response = request.json()
    print(response['routes'][0])
    result = {}
    result['distance'] = response['routes'][0]['distance'] /1000
    result['travel_coordinates'] = polyline.decode(response['routes'][0]['geometry'])
    result['cost'] = result['distance'] * car_cost_per_km
    result['co2g'] = result['distance'] * car_co2g_per_km
    result['duration'] = response['routes'][0]['duration'] / 60
    
    print(result)

    return


