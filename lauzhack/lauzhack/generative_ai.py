import time
from openai import OpenAI
from google_images_search import GoogleImagesSearch
import json
import os

from . import geocoding

openai_key = ""
try:
    with open(os.path.join(os.path.dirname(__file__),"..","..","keys", 'openai_key.txt'), 'r') as file:
        openai_key = file.read()
except Exception as e:
        print(e)


google_api_key = ""
try:
    with open(os.path.join(os.path.dirname(__file__),"..","..","keys", 'google_api_key.txt'), 'r') as file:
        google_api_key = file.read()
except Exception as e:
        print(e)

google_cse = ""
try:
    with open(os.path.join(os.path.dirname(__file__),"..","..","keys", 'google_cse_key.txt'), 'r') as file:
        google_cse = file.read()
except Exception as e:
        print(e)

client = OpenAI(
        api_key=openai_key,
    )


schema = {
      "type": "object",
      "properties": {
           "results": {
                "type": "array",
                "items": {
                     "type": "object",
                     "properties": {
                          "name": {
                               "type": "string"
                          },
                          "lat": {
                               "type": "string"
                          },
                            "lon": {
                                 "type": "string"
                            },
                          "description": {
                               "type": "string"
                          },
                            
                     },
                     "required": [
                          "name",
                            "lat",
                            "lon",
                          "description"
                          
                     ]
                }
           }

      
}
}

def get_images(query):
    gis = GoogleImagesSearch(google_api_key, google_cse)
    _search_params = {
        'q': query,
        'num': 1,
        'fileType': 'jpg|gif|png',
        'imgType': 'photo',
        'searchType': 'image',
    }
    gis.search(search_params=_search_params)
    for image in gis.results():
        return image.url
    
def generate_response(prompt,lat,lon) -> json:   
    systemPrompt = "You are travel advisor in Switzerland. The client will describe their preferences and you will suggest a place to visit. Return up to 5 results."
    
   
    
    if lat is not None and lon is not None:
        location = geocoding.geo_decode(lat, lon)
        print(location)
        systemPrompt += f"You should prioritize places that are close to {location}."
         

    start = time.time()
    completion = client.chat.completions.create(
    messages=[
    {"role": "system", "content": systemPrompt },
    {"role": "user", "content": prompt},
  ],
    model="gpt-3.5-turbo",
  functions= [{ 'name': "set_recipe", 'parameters': schema }],
      function_call= {'name': "set_recipe"}
)
    print(f"Time to generate: {time.time() - start}s")

    
    query_results = json.loads(completion.choices[0].message.function_call.arguments)
    results = []

    print(f"Query results: {query_results}")
    if 'results' not in query_results:
         return generate_response(prompt,lat,lon)
    
    for result in query_results['results']:
        r = {}
        r['name'] = result['name']
        r['description'] = result['description']

        r['coordinates'] = [result['lon'], result['lat']]
        print(r['coordinates'])
        image = get_images(result['name'])
        r['image'] = image
        results.append(r)
        
       
    return results

