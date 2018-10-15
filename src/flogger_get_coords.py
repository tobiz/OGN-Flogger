#
# Function to determine latitude, longitude and elevation given location place name details.
# Details are returned as a list.
# For example if called as:
# loc = get_coords("My Gliding Club UK")
#   then:
#        latitude = loc[0], longitude = loc[1], elevation = loc[2]
#
#20181010    This has a problem that google geocoder API now needs a Key to get elevation data. For now it has to be supplied
#            in the GUI field. The elevation can be found using: https://www.freemaptools.com/elevation-finder.htm
# 
from geopy.geocoders import Nominatim
import geocoder
from geopy.exc import GeocoderTimedOut 
import time
from geopy.geocoders.base import ERROR_CODE_MAP
import geopy
from geopy import geocoders
import requests
import json

def get_coords(address, settings):
    print "get_coords called with: ", address
        
    geolocator = Nominatim()
#    g = geolocator.geocode()
    place, (lat, lng) = geolocator.geocode(address, exactly_one=True, timeout=10)
    print "%s: %.5f, %.5f" % (place, lat, lng)
#    
#    if settings.FLOGGER_QNH <> "":
#        return lat, lng, settings.FLOGGER_QNH   
#    print "Call requests"
#    lng = str(-1.20930940595)
#    lat = str(54.2289539)
    url = "https://elevation-api.io/api/elevation?points=(" + str(lat) + "," + str(lng)
#    print "url string is: ", url
    jsondata = requests.get(url)
    x = json.loads(jsondata.text)
    alt =  x["elevations"][0]["elevation"]
#    print type(alt)
#    print "elevation is: ", alt
    return lat, lng, alt
    #
    # Following doesn't work after Google changed charging policy
    #
    ele = geocoder.google([lat, lng], method='elevation')
    print address, " Elevation is: ", ele.meters
    try:
        geolocator = Nominatim(user_agent="OGN_Flogger")
        try:   
            location = geolocator.geocode(address, timeout=5, exactly_one=True)  # Only 1 location for this address
#            location = geocoder.google(address, timeout=5, exactly_one=True)  # Only 1 location for this address
            if location == None:
                print "Geocoder Service timed out or Airfield: ", address, " not known by geocode locator service. Check settings"
                return False
#            print address, " Is at: ", location.latlng
            print address, " Is at: ", " Lat: ", location.latitude, " Long: ", location.longitude, " Alt: ", location.altitude
            
            i = 1
            while i <= 5:
#                ele = geocoder.google([location.latitude, location.longitude], method='elevation', key="AIzaSyA6FEQW_6e5Va0bUd9BHqTLUWEqFmKOSXg")
                ele = geocoder.bing([location.latitude, location.longitude], method="reverse")
                print "OSM returned: ", ele
                if ele.meters == None:
                    print "geocoder.google try: ", i
                    i = i + 1
                    time.sleep(1)
                    continue
                else:
                    print "Geolocator worked for: ", address, " Lat: ", location.latitude, " Long: ", location.longitude, " Ele: ",ele.meters
                    return location.latitude, location.longitude, ele.meters
                print "Geolocator failed for: ", address, " Lat: ", location.latitude, " Long: ", location.longitude, " Ele: ", ele.meters, "Try a Restart" 
                exit(2)
            
        except ERROR_CODE_MAP[400]:
            print " ERROR_CODE_MAP is: ",  ERROR_CODE_MAP[400]
        except ERROR_CODE_MAP[401]:
            print " ERROR_CODE_MAP is: ",  ERROR_CODE_MAP[401]
        except ERROR_CODE_MAP[402]:
            print " ERROR_CODE_MAP is: ",  ERROR_CODE_MAP[402]
        except ERROR_CODE_MAP[403]:
            print " ERROR_CODE_MAP is: ",  ERROR_CODE_MAP[403]
        except ERROR_CODE_MAP[407]:
            print " ERROR_CODE_MAP is: ",  ERROR_CODE_MAP[407]
        except ERROR_CODE_MAP[412]:
            print " ERROR_CODE_MAP is: ",  ERROR_CODE_MAP[412]
        except ERROR_CODE_MAP[413]:
            print " ERROR_CODE_MAP is: ",  ERROR_CODE_MAP[413]
        except ERROR_CODE_MAP[414]:
            print " ERROR_CODE_MAP is: ",  ERROR_CODE_MAP[414]
        except ERROR_CODE_MAP[502]:
            print " ERROR_CODE_MAP is: ",  ERROR_CODE_MAP[502]
        except ERROR_CODE_MAP[503]:
            print " ERROR_CODE_MAP is: ",  ERROR_CODE_MAP[503]
        except ERROR_CODE_MAP[504]:
            print " ERROR_CODE_MAP is: ",  ERROR_CODE_MAP[503]
        return False
    except GeocoderTimedOut as e:
        print "Geocoder Service timed out for Airfield: ", address
        return False
