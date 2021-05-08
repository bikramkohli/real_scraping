import googlemaps
from datetime import datetime
import re

gmaps = googlemaps.Client(key='AIzaSyDXuFSMcQvP9pQ7wZwf-Oz3X5I6MFvelfQ')

# Geocoding an address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit
now = datetime.now()
directions_result = gmaps.directions("Woodland Hills Rd Abingdon, VA 24210",
                                     "Fairfax, VA",
                                     mode="driving",
                                     departure_time=now)
def match_test(regex, text):
    # Gives a list of all complete matches
    ans = ''
    for match in regex.finditer(text):
        ans += match.group(0)
    return ans

directionsRE = re.compile(r'duration\':[a-z\'\{\:]+')
print(directions_result[0].get('legs')[0].get('duration').get('text'))
print(directions_result[0].keys())
