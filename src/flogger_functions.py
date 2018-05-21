#
# 20150903:      First working version
# Usage:         This module consists of the main functions used by flogger.py
#                It's a separate module to keep the size of flogger.py more manageable 
#
# 20160513:        This is a bit of a mess!! It should now be updated to contain all the functions
#                in flogger.py as these are more up to date.  The functions in flogger.py should
#                then be deleted.
#

import socket
#from libfap import *
import flogger_settings
import string
import datetime
import time
import sqlite3
import pytz
from datetime import timedelta
import sys
from flarm_db import flarmdb
from pysqlite2 import dbapi2 as sqlite
from open_db import opendb 
import ephem
#from flogger_process_log_old import process_log
import argparse
from flogger_dump_flights import dump_flights
#from flogger_dump_tracks import dump_tracks
from flogger_get_coords import get_coords
import os

def CheckPrev(callsignKey, dataKey, value):
    #    
    #-----------------------------------------------------------------
    # Checks whether nprev_vals exist, if not creates an initial set for callsignKey   
    #-----------------------------------------------------------------
    #
    print "CheckPrev if callsign in nprev_vals: ", callsignKey, " key: ", dataKey, " Value: ", value 
    if nprev_vals.has_key(callsignKey) == 1:
        print "nprev_vals already has entry: ", callsignKey
    else:
        print "nprev_vals doesn't exist for callsignKey: ", callsignKey
        nprev_vals[callsignKey] = {}
        nprev_vals[callsignKey] = {'latitude': 0, 'longitude': 0, "altitude": 0, "speed": 0, 'maxA': 0}
        nprev_vals[callsignKey][dataKey] = value
        print "nprev_vals for callsignKey: ", callsignKey, " is: ", nprev_vals[callsignKey]
#        print "nprev_vals is now: ", nprev_vals
    return

def CheckVals(callsignKey, dataKey, value):
    #    
    #-----------------------------------------------------------------
    # Checks whether nvalues exist, if not creates an initial set for callsignKey   
    #-----------------------------------------------------------------
    #
    print "CheckVals if callsign in nvalues: ", callsignKey, " key: ", dataKey, " Value: ", value 
    if nvalues.has_key(callsignKey) == 1:
        print "nvalues already has entry: ", callsignKey
    else:
        print "nvalues doesn't exist for callsignKey: ", callsignKey
        nvalues[callsignKey] = {}
        nvalues[callsignKey] = {'latitude': 0, 'longitude': 0, "altitude": 0, "speed": 0, 'maxA': 0}
        nvalues[callsignKey][dataKey] = value
        print "nvalues for callsignKey: ", callsignKey, " is: ", nvalues[callsignKey]
#        print "nvalues is now: ", nvalues
    return

def isDayLight ():
    return True

def fleet_check(call_sign):
    #    
    #-----------------------------------------------------------------
    # Checks whether table aircraft has entry for call_sign, return True or False   
    #-----------------------------------------------------------------
    #
    if aircraft.has_key(call_sign):
        return True
    else:
        return False
    
def comp_vals(set1, set2):
    #    
    #----------------------------------------------------------------- 
    # Works out if the difference in positions is small and both speeds are close to zero
    # Return True is yes and False if no
    # Set1 are new values, set2 old values
    #-----------------------------------------------------------------
    #
    print "Set1 value for key latitude is: ", set1["latitude"], " value: ", float(set1["latitude"])
    delta_latitude = float(set1["latitude"]) - float(set2["latitude"])
    delta_longitude = float(set1["longitude"]) - float(set2["longitude"])
    delta_altitude = float(set1["altitude"]) - float(set2["altitude"])
    delta_speed = float(set1["speed"]) - float(set2["speed"])
    print "Delta positions. Lat: ", delta_latitude, " Long: ", delta_longitude, " Alt: ", delta_altitude, " Speed: ", delta_speed 
#     if (delta_latitude < L_SMALL) and (delta_longitude < L_SMALL) and (delta_altitude < A_SMALL) and (delta_speed < V_SMALL):
    if delta_speed <> 0.0:
        print "Delta speed not zero, check others"
#     if (delta_latitude == 0.0) and (delta_longitude == 0.0) and (delta_altitude == 0.0) and (delta_speed == 0.0):
        if (delta_latitude == 0.0) and (delta_longitude == 0.0) and (delta_altitude == 0.0):
            print "Positions same"
            return True
        else:
            print "Positions different"
            return False
    else:
        print "Delta speed zero, return same"
        return True
    
def set_keepalive(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    #    
    #-----------------------------------------------------------------
    # Sets up supplied keepalive values for the specified socket 
    # It activates after 1 second (after_idle_sec) of idleness,
    # then sends a keepalive ping once every 3 seconds (interval_sec),
    # and closes the connection after 5 failed ping (max_fails), or 15 seconds 
    #-----------------------------------------------------------------
    #
    print "set_keepalive for idle after: ", after_idle_sec
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)
    return
    

def is_dst(zonename):
    # Determine if in daylight
    tz = pytz.timezone(zonename)
    now = pytz.utc.localize(datetime.utcnow())
    return now.astimezone(tz).dst() != timedelta(0)
   
def fleet_check_new(callsign):
    #    
    #-----------------------------------------------------------------
    # Checks whether supplied callsign is in the aircraft table  
    #-----------------------------------------------------------------
    #
    print "Function fleet_check_new"
    print "In fleet check for: ", callsign
    cursor.execute('''SELECT ROWID FROM aircraft WHERE registration =? or flarm_id=? ''', (callsign, callsign,))
    row = cursor.fetchone()
#    cursor.execute('''SELECT ROWID FROM flarm_db WHERE registration =?''', (callsign,))
    flarm_id = callsign[3:]
    print "search for flarm_id: ", flarm_id
#    cursor.execute('''SELECT ROWID FROM flarm_db WHERE flarm_id =?''', (callsign,))
    cursor.execute('''SELECT ROWID FROM flarm_db WHERE flarm_id =?''', (flarm_id,))
    row1 = cursor.fetchone()
    if row1 == None:
        print "Registration not found in flarm_db: ", callsign
    else:
        print "Aircraft: ", callsign, " found in flarm db at: ", row1[0] 
    # Temporarily use local aircraft db   
    if row <> None:
        print "Aircraft: ", callsign, " found in aircraft db: ", row[0]
        return True
    else:
        print "Aircraft: ", callsign, " not found insert in local aircraft db"
        cursor.execute('''INSERT INTO aircraft(registration,type,model,owner,airfield ,flarm_id)
                            VALUES(:registration,:type,:model,:owner,:airfield,:flarm_id)''',
                            {'registration':callsign, 'type':"", 'model': "", 'owner':"", 'airfield': settings.FLOGGER_AIRFIELD_NAME, 'flarm_id':callsign})
        return True
    
def callsign_trans(callsign):
    #
    #-----------------------------------------------------------------
    # Translates a callsign supplied as a flarm_id
    # into the aircraft registration using a local db based on flarmnet
    # If in flarmnet db then returns the aircraft registration from there, else
    # returns the original callsign 
    #-----------------------------------------------------------------
    #
    print "Function callsing_trans"
    # Old version
#    cursor.execute('''SELECT registration, flarm_id FROM aircraft WHERE registration =? or flarm_id=? ''', (callsign, callsign,))
#    if callsign.startswith("FLR"):
        # Callsign starts with "FLR" so remove it
#        callsign = "%s" % callsign[3:]
#        print "Removing FLR string.  Callsign is now: ", callsign
#    cursor.execute('''SELECT registration FROM flarm_db WHERE flarm_id=? ''', (callsign,))
#    row = cursor.fetchone()   
#    if row <> None:
        # Registration found for flarm_id so return registration
#        registration = "%s" % row
#       print "In flarmnet db return: ", registration
#        return registration
#    else:
        # Registration not found for flarm_id so return flarm_id
#        print "Not in flarmnet db return: ", callsign
#        return callsign
    
    cursor.execute('''SELECT registration, flarm_id FROM aircraft WHERE registration =? or flarm_id=? ''', (callsign,callsign,))
    if callsign.startswith("FLR") or callsign.startswith("ICA") :
        # Callsign starts with "FLR" or ICA so remove it
        str = callsign[3:]
        ncallsign = "%s" % str
        print "Removing FLR or ICA string.  Callsign is now: ", ncallsign
    cursor.execute('''SELECT registration FROM flarm_db WHERE flarm_id=? ''', (ncallsign,))
    row = cursor.fetchone() 
    if row <> None:
        # Registration found for flarm_id so return registration
        registration = "%s" % row
        print "In flarm db return: ", registration
        return registration
    else:
        # Registration not found for flarm_id so return flarm_id
        print "Not in flarm db return: ", callsign
        return ncallsign
    
def APRS_connect (settings):
    #    
    #-----------------------------------------------------------------
    # Connect to the APRS server to receive flarm data    
    #-----------------------------------------------------------------
    #
    
    # create socket & connect to server
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        set_keepalive(sock, after_idle_sec=60, interval_sec=3, max_fails=5)
        sock.connect((settings.APRS_SERVER_HOST, settings.APRS_SERVER_PORT))
    except Exception, e:
        print "Socket failure on connect: ", e
    print "Socket sock connected"
    
    try:
        s = "user %s pass %s vers OGN_Flogger 0.2.2 filter r/%s/%s/25\n " % (settings.APRS_USER, settings.APRS_PASSCODE, settings.FLOGGER_LATITUDE, settings.FLOGGER_LONGITUDE)
#        print "Socket connect string is: ", s
        sock.send(s)
    except Exception, e:
        print "Socket send failure: ", e
        exit()
    print "Socket send ok"
    
    # Make the connection to the server
#    start_time = datetime.datetime.now()
#    keepalive_time = time.time()
#    sock_file = sock.makefile()
    print "APRS connection made"
    return sock


def addTrack(cursor, flight_no, track_no, longitude, latitude, altitude, course, speed, timeStamp):
    #    
    #-----------------------------------------------------------------
    # Add gps track data to track record if settings.FLOGGER_TRACK is "Y" ie yes    
    #-----------------------------------------------------------------
    #
    dt = str(datetime.datetime.now())  # Get the datetime this track point is created as string
    sdt = dt[0:10] + "T" + dt[11:19] + "Z"  # Convert to string format for gpx, ie YYYY-MM-DDTHH:MM:SSZ

    if settings.FLOGGER_TRACKS == "Y":
        print "Adding track data to: %i, %i, %f, %f, %f, %f %f " % (flight_no, track_no, latitude, longitude, altitude, course, speed)
        cursor.execute('''INSERT INTO track(flight_no,track_no,latitude,longitude,altitude,course,speed,timeStamp) 
            VALUES(:flight_no,:track_no,:latitude,:longitude,:altitude,:course,:speed,:timeStamp)''',
            {'flight_no':flight_no, 'track_no':track_no, 'latitude':latitude, 'longitude':longitude, 'altitude':altitude, 'course':course, 'speed':speed, 'timeStamp':timeStamp})
    return
    
def endTrack():
    return

def CheckTrackData(cursor, callsignKey):
    #    
    #-----------------------------------------------------------------
    # This checks whether a recorded for the callsignKey has been created
    # in the flight_log2 table. Not used at the moment
    #-----------------------------------------------------------------
    #
    
    print "check flight_no if callsign in flight_no{}: ", callsignKey 
    if flight_no.has_key(callsignKey) == True:
        print "flight_no already has entry: ", callsignKey
    else:
        try:
            cursor.execute('''SELECT max(id) FROM flight_log2 WHERE src_callsign =?''', (callsignKey,))
        except:
            print "!!!ERROR - No record in flight_log2 for: ", callsignKey
            # If this fails then need to think about adding record for flight_log2, but why?
            exit()
        row_id = cursor.fetchone()[0]  # value of id for row just inserted use as flight_no for flight
        print "Last row ID of flight_log2 for callsign: ", callsignKey, " inserted was: ", row_id
        flight_no[src_callsign] = row_id
        track_no[callsignKey] = 1
        print "flight_no for callsignKey: ", callsignKey, " is: ", flight_no[callsignKey]
    return  True

def delete_table (table): 
    #    
    #-----------------------------------------------------------------
    # This function deletes the SQLite3 table 
    # with the name supplied by "table".
    #-----------------------------------------------------------------
    #
    parm = "DELETE FROM %s" % (table)
    try:
        cursor.execute(parm)
        print "New Delete %s table ok" % (table)
    except:
        print "New Delete %s table failed or no records in tables" % (table)      
    return
