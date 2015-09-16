#http://stackoverflow.com/questions/14580540/get-location-coordinates-using-bing-or-google-api-in-python
import urllib
import json

def get_coordinates(address, from_sensor=False, googleGeocodeUrl='http://maps.googleapis.com/maps/api/geocode/json?'):
    query = query.encode('utf-8')
    params = {
        'address': address,
        'sensor': "true" if from_sensor else "false"
    }
    url = googleGeocodeUrl + urllib.urlencode(params)
    json_response = urllib.urlopen(url)
    response = json.loads(json_response.read())
    if response['results']:
        location = response['results'][0]['geometry']['location']
        latitude, longitude = location['lat'], location['lng']
    else:
        latitude, longitude = None, None
        print address, "<no results>"
    return latitude, longitude

