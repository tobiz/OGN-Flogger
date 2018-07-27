import aprslib
from aprslib import string_type_parse
from aprslib.exceptions import (UnknownFormat, ParseError)
from aprslib.parsing.common import *
from aprslib.parsing.misc import *
from aprslib.parsing.position import *
from aprslib.parsing.mice import *
from aprslib.parsing.message import *
from aprslib.parsing.telemetry import *
from aprslib.parsing.weather import *
from flogger_settings import *
global settings

def aprs_parse(packet, settings):
#    print "aprs_parse called: ", packet
    try:
        p_dict = aprslib.parse(packet)
        res = check_parse(p_dict, settings)
        if res == False:
            return False
    except ParseError as msg:
#        print "aprs_parse failed: ", packet
        return False
#    print "aprs_parse worked"
    return res

def test_base(via_name, settings):
#    print "test_base called: ", via_name
    for base_name in settings.FLOGGER_APRS_BASES:
        if base_name == via_name:
#            print "via_name found: ", via_name
            return True
    return False

def check_parse(parse_dict, settings):
#    print "check_parse called: ", parse_dict
    try:
        comment = parse_dict["comment"]
#        print "comment field is: ", comment
        # Check comment field is not empty string
        if comment <> "":         
            # check via is one of the base stations in Flogger config
            via = parse_dict["via"]
            if test_base(via, settings):
#                print "via found and on list of base stations: ", via
                return {"from": parse_dict["from"], 
                        "longitude": parse_dict["longitude"], 
                        "latitude": parse_dict["latitude"], 
                        "altitude": parse_dict["altitude"],
                        "speed": parse_dict["speed"], 
                        "course": parse_dict["course"],
                        "timestamp": parse_dict["timestamp"],
                        }
#            print "via key not present in parse dictionary"
            return False
    except:
#        print "comment key not in parse dictionary"
        return False

        
        
        
    