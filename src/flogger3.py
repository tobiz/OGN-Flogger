#
# FLOGGER
#
# This program reads records from the OGN network processing only
# those received from a specified site and registration marks, eg aircraft belonging to 
# a specific club.
# It writes each record to a database and at the end of each day process
# them to determine the flight times of each flight for each machine.
# Phase 1 will just collect the data. 
# Phase 2 will process the data into a new table
# Phase 3 will then format that information with the intention of
#         it being used to be checked against the manual log books.
# Phase 4 will remove old flight and track file older than a certain date
# The intention is that it will collect the data between the hours of daylight, 
# producing the summary at the end of the day.
# This program could be run on a Raspberry Pi as it is so low powered
#
# Altitude in metres.
# Land speed in km/h.
# Latitude, west is negative decimal degrees.
# Longitude, south is negative decimal degrees.
#
# This program is covered by the GNU GENERAL PUBLIC LICENSE.
# See the file 'LICENSE' for details
# 
#
# 20150312:     First working version
# Usage:         Run flogger.py to collect the daily flight data then
#                run process.py which processes the raw data into a table flights in the database flogger.sgl3
#                This first version is very experimental, it is proof of concept and processes. The code needs to
#                be 'improved'.
# To be done:    1) The program should be run each day between 0900 and sunset. This should be handled by cron
#                   to start the program at a time specified in settings which then calculates sunrise and suspends
#                  until then.  Once running the program determines sunset and stopping itself at that time. It also needs
#                   to handle power outages (not sure how at the moment)
#                2) The Flarm code to registration code needs to addressed using OGNs new database.
# 20150505        Second working version
#                Only need to run flogger.py, it now handles collection of data during daylight hours and processes
#                after sunset (assumes gliders only fly during daylight hours)
#                Now reads aircraft registration data from Flarmnet to build own internal table
# 20150515        Third working version
#                1) APRS user and APRS passcode have to be supplied on the command line and not in settings
#                2) Changes to flogger_process_log_old to correct errors - still in testing
#
# 20150520        Fourth working version (V0.1.0)
#                1) On aircraft stop set altitude to initial value else highest value for any flight of the day
#                   will be the one compared against as the maximum and not the max for a specific flight.
#                   Bug 20150520-1 Assigned
#                2) Flights table only contains flights for one day and not all previous days flights
#                   Bug 20150520-2 Assigned
#
# 20150527        Fifth working version (V0.1.1)
#                Test version for:
#                1) Bug 20150520-1
#                2) Bug 20150520-2
#
# 20150529        First beta test version (V0.2.0)
#                1) Bug 20150520-1    Solved
#                2) Bug 20150520-2    Solved
#                3) Enhancement - dump days flights table as .csv file
#
# 20150530        Correction to first beta test version (V0.2.1)
#                1) Correction to dump flights to .csv - to make it work!
#
# 20150604        Added enhancements to version V0.2 (V0.2.2)
#                1) Allowance for short duration flight
#                2) Use of geocoding to determine airfield position data - proposed by D.Spreitz
#
# To be done:    1) Tidy up code, remove all redundant testing comments
#                2) A lot more testing - some features might still not work!
#                3) Consider how this may be run as a service with standard start, stop etc options
#                4) Consider adding full logging with levels
#                5) Review the algorithm to determine if aircraft is on the ground. At the moment it determines
#                   this by the GPS ground speed being zero (ie below a defined value); the ground speed could be zero
#                   if the wind speed and airspeed are the same but opposite, eg when ridge flying. The algorithm could use
#                   the altitude as well, eg if ground speed is zero but altitude is greater than home airfield altitude then
#                   'we're flying'. Note this still has issues!
#                6) Need to consider sending 'keep alives' when in the sleep state. Solved, not needed
#                7) There's a problem concerning character codes when building the flarm database which needs solving, only show in 1 record
#
# 20160208        1) Add modification to sequence tracks per flight by flarm record timestamp.  Using multiple beacons can result in
#                    track points that are out of sequence when based on order received due to Internet time delays, hence
#                    use the GPS timestamp recorded in the data taken and sent by flarm (assumes timestamp is from Flarm!).
#                 2) Also added graceful exit on Cntrl-C
#
# 20160323        1) Added optional output of track data in IGC format
#                 2) Added optional deletion of old flight .csv and track .csv/.igc files
#
# 20160514        1) Use $ pipreqs --force /path/to/project to generate requirements.txt for pip install
#
# 20160518        1) Added attempt to load earlier version Linux libfap if current fails
#
# 20161026        1) Added flogger_find_tug code. This tries to determine which tug, if any, launched a particular glider.
#                    Note this doesn't always get the right result, but then nor does OGN Flight Log! This could be due to tugs 
#                    sometimes powering down if a launch is not imminent. Gliders are likely to be always powered on and Flarm operating.
#                    Hence when it becomes time to launch the tug powers up, Flarm is now on but takes some time for the signal to be
#                    acquired and put onto and processed by the APRS system. It is therefore possible for the launch to take place
#                    with the take-off times for tug and glider to be too far displaced (from the APRS data) for flogger-find-tug 
#                    to determine the launch has happened. The solution is possibly to increase the time delta used between glider and 
#                    tug take-off but this could result in false positives, some fine tuning maybe needed. Interested to know if
#                    OGN Flight Log has similar reasoning.
#
# 20161108        1) Rewrote phase 2 flight log processing to be much simpler. Phase 2 puts flights into the flight_group
#                    table such that all flights by a single aircraft have the same group id. This enables each flight to
#                    be determined to be a distinct flight from its predecessor or not.
#
# 20170201:        1) Added simple function test_YorN to test for Y|y or N|n
#                  2) Started developing using Eclipse Neon.2 (4.6.2)
#


import socket
#from libfap import *
#import flogger_settings
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
#from flogger_process_log import process_log
import argparse
from flogger_dump_flights import dump_flights
from flogger_dump_tracks import dump_tracks2
from flogger_get_coords import get_coords
from flogger_signals import sig_handler
import signal
import os
import os.path
from flogger_dump_IGC import dump_IGC
from flogger_email_log import email_log2
from flogger_landout import landout_check
from geopy.distance import vincenty
from flogger_email_msg import email_msg
from flogger_find_tug import find_tug
from flogger_test_YorN import test_YorN
from flogger_gui import *

from flogger_settings import * 
from threading import Thread
from flogger_aprs_parser import  *
from flogger_process_log import *
from flogger_path_join import *
#
# This added to make it simpler after going to gui version
#
global settings

class flogger3(MyApp):
    
    def __init__(self, interval=1):
        print "init flogger3"
        print "flogger3 initialized"
        return
    
    def flogger_run(self, settings):
        print "flogger_run called"
        print "settings.FLOGGER_SMTP_SERVER_URL: ", settings.FLOGGER_SMTP_SERVER_URL
#        print "settings.FLOGGER_SMTP_SERVER_PORT: ", settings.FLOGGER_SMTP_SERVER_PORT
#        print "settings.FLOGGER_DB_SCHEMA: ", settings.FLOGGER_DB_SCHEMA
        self.thread = Thread(target=self.flogger_start, name= "flogger", args=(settings,))
        print "Thread setup"
        self.thread.daemon = True                            # Daemonize thread
        self.thread.start()
        print "flogger thread running"
        return
    
    def floggerStop(self):
        print "floggerStop called"
#        libfap_cleanup()
        return
    #    def flogger_start(self, settings):
#    def flogger_start(self, settings):
    def flogger_start(self, local_settings):
        print "flogger_start called\n"
        settings = local_settings
#        print "settings.FLOGGER_SMTP_SERVER_URL: ", settings.FLOGGER_SMTP_SERVER_URL
#        print "settings.FLOGGER_SMTP_SERVER_PORT: ", settings.FLOGGER_SMTP_SERVER_PORT
#        print "settings.FLOGGER_DB_SCHEMA: ", settings.FLOGGER_DB_SCHEMA

        prev_vals = {'latitude': 0, 'longitude': 0, "altitude": 0, "speed": 0}
        nprev_vals =     {"G-CKLW": {'latitude': 0, 'longitude': 0, "altitude": 0, "speed": 0, 'maxA': 0},
                         "G-CKFN": {'latitude': 0, 'longitude': 0, "altitude": 0, "speed": 0, 'maxA': 0}
                         }
        values = {'latitude': 0, 'longitude': 0, "altitude": 0, "speed": 0}
        nvalues =     {"G-CKLW": {'latitude': 0, 'longitude': 0, "altitude": 0, "speed": 0, 'maxA': 0},
                     "G-CKFN": {'latitude': 0, 'longitude': 0, "altitude": 0, "speed": 0, 'maxA': 0}
                        }
            
        L_SMALL = float(0.001)                            # Small latitude or longitude delta of a 0.001 degree
        A_SMALL = float(0.01)                             # Small altitude delta of 0.01 a metre, ie 1cm
        V_SMALL = float(settings.FLOGGER_V_SMALL)         # Small velocity delta of 10.0 kph counts as zero ie not moving
        V_TAKEOFF_MIN = float(settings.FLOGGER_V_TAKEOFF_MIN)
        V_LANDING_MIN = float(settings.FLOGGER_V_LANDING_MIN)
        frst_time = False
        AIRFIELD = "SuttonBnk"
        flight_no = {}                                      # A dictionary {callsign: flight_no}
        track_no = {}                                       # A dictionary {callsign: track_no}
        # Coded     001-099: Gliders, 
        #             101-199: Tugs, 
        #             201-299: Motor Gliders, 
        #             301-399: Other
        aircraft = {"G-CKLW": 1, "G-CKLN": 2, "G-CJVZ": 3, "G-CHEF": 4, "G-CKFN": 5,
                    "G-CHVR": 6, "G-CKJH": 7, "G-CKRN": 8, "G-CGBK": 9, "G-CDKC": 10,
                    "G-BFRY": 101, "G-BJIV": 102, "G-MOYR": 103,
                    "G-OSUT": 201,
                    "FLRDDF9C4": 301, "FLRDDE5FC": 302, "FLRDDBF13": 303, "FLRDDA884": 304, "FLRDDA886": 305, "FLRDDACAE": 306, "FLRDDA7E9": 307,
                    "FLRDDABF7": 308, "FLRDDE671": 309} 
        
        
        def CheckPrev(callsignKey, dataKey, value):
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
            if aircraft.has_key(call_sign):
                return True
            else:
                return False
            
        def comp_vals(set1, set2):
            # Works out if the difference in positions is small and both speeds are close to zero
            # Return True is yes and False if no
            # Set1 are new values, set2 old values
            print "Set1 value for key latitude is: ", set1["latitude"], " value: ", float(set1["latitude"])
        #     lat1 = float(set1["latitude"])
        #     lat2 = float(set2["latitude"])
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
            """Set TCP keepalive on an open socket.
        
            It activates after 1 second (after_idle_sec) of idleness,
            then sends a keepalive ping once every 3 seconds (interval_sec),
            and closes the connection after 5 failed ping (max_fails), or 15 seconds
            """
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
            # This has become a little confusing! If FLOGGER_FLEET_CHECK == n|N then FLOGGER_AIRFIELD_NAME is not used in
            # the flarm_db search so a non-fleet aircraft can be found, but the later code checks whether the aircraft
            # has taken off at FLOGGER_AIRFIELD_NAME; if it hasn't it won't be included in the flights, if it has it will.
            #
            # This logic and code needs to be re-thought!
            # Note, there is a difference between aircraft registered to a location and in a designated 'fleet' for
            # that location and whether the aircraft has taken off from a location.
            # The fleet_check is intended to check whether an aircraft is a member of a designated fleet, not whether
            # it has taken off from the designated location. The intention if the fleet check is to enable recording only
            # flights undertaken by the club fleet.
            #
            print "In fleet check for: ", callsign
        #    cursor.execute('''SELECT ROWID FROM aircraft WHERE registration =? or flarm_id=? ''', (callsign,callsign,))
        #    row = cursor.fetchone()
        #    flarm_id = callsign[3:]
        #    print "search for flarm_id: ", flarm_id
        #    cursor.execute('''SELECT ROWID FROM flarm_db WHERE flarm_id =?''', (flarm_id,))
        #    if settings.FLOGGER_FLEET_CHECK == "N" or settings.FLOGGER_FLEET_CHECK == "n":
            if not test_YorN(settings.FLOGGER_FLEET_CHECK):
                print "Fleet Check: ", settings.FLOGGER_FLEET_CHECK
                fleet_name = "Fleet Name: Not used"
                cursor.execute('''SELECT ROWID, registration FROM flarm_db WHERE registration =? OR flarm_id =? ''', (callsign,callsign[3:],))
            else:
                print "Fleet Check for Airfield: ", settings.FLOGGER_AIRFIELD_NAME
                fleet_name = settings.FLOGGER_AIRFIELD_NAME
                cursor.execute('''SELECT ROWID FROM flarm_db WHERE registration =? OR flarm_id =? AND airport=?''', (callsign,callsign[3:],settings.FLOGGER_AIRFIELD_NAME,))
            #cursor.execute('''SELECT ROWID FROM flarm_db WHERE registration =? OR flarm_id =? AND airport=?''', (callsign,callsign[3:],settings.FLOGGER_AIRFIELD_NAME,))
            row1 = cursor.fetchone()
            if row1 == None:
                print "Registration not found in flarm_db: ", callsign, " for: ", fleet_name
                return False
            else:
                print "Aircraft: ", callsign, " found in flarm db at: ", row1[0], " for: ", fleet_name
                reg = callsign_trans(callsign)
        #        if settings.FLOGGER_FLEET_CHECK <> "N":
                print "settings.FLOGGER_FLEET_CHECK: ", settings.FLOGGER_FLEET_CHECK
#                if not test_YorN(settings.FLOGGER_FLEET_CHECK):
                if test_YorN(settings.FLOGGER_FLEET_CHECK):
        #            if settings.FLOGGER_FLEET_LIST[reg] > 100 and settings.FLOGGER_FLEET_LIST[reg] < 200 and settings.FLOGGER_LOG_TUGS == "N":
                    if settings.FLOGGER_FLEET_LIST[reg] > 100 and settings.FLOGGER_FLEET_LIST[reg] < 200 and (not test_YorN(settings.FLOGGER_LOG_TUGS)):
                        print "Don't log tug: %s" % reg
                        return False
                    else:
                        print "Tug flight: ", reg
            # At least 1 match for the callsign has been found
            return True
        
            
        def callsign_trans(callsign):
            # Translates a callsign supplied as a flarm_id
            # into the aircraft registration using a local db based on flarmnet or OGN
            # Note if OGN db is being used then callsigns don't start with FLR or ICA, this is denoted by the 'Type' field
        #    cursor.execute('''SELECT registration, flarm_id FROM aircraft WHERE registration =? or flarm_id=? ''', (callsign,callsign,))
            if callsign.startswith("FLR") or callsign.startswith("ICA") :
                # Callsign starts with "FLR" or ICA so remove it
                str = callsign[3:]
                ncallsign = "%s" % str
                print "Removing FLR or ICA string.  Callsign is now: ", ncallsign
            else:
                ncallsign = "%s" % callsign
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
        #        sock.send('user %s pass %s vers OGN_Flogger 0.0.2 filter r/+54.228833/-1.209639/25\n ' % (settings.APRS_USER, settings.APRS_PASSCODE))
        
                APRSparm = ('user %s pass %s vers %s %s filter r/%s/%s/%s\n ' % (settings.APRS_USER, 
                                                                                settings.APRS_PASSCODE, 
                                                                                settings.FLOGGER_NAME, 
                                                                                settings.FLOGGER_VER, 
                                                                                settings.FLOGGER_LATITUDE, 
                                                                                settings.FLOGGER_LONGITUDE, 
                                                                                settings.FLOGGER_RAD)) 
        #        print "APRSparm is: ", APRSparm  
        #        s = "user %s pass %s vers OGN_Flogger 0.2.2 filter r/%s/%s/25\n " % (settings.APRS_USER, settings.APRS_PASSCODE, settings.FLOGGER_LATITUDE, settings.FLOGGER_LONGITUDE)
        #        print "Socket connect string is: ", s
                sock.send(APRSparm)
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
        
        
        def addTrack(cursor,flight_no,track_no,longitude,latitude,altitude,course,speed,timeStamp):
            #    
            #-----------------------------------------------------------------
            # Add gps track data to track record if settings.FLOGGER_TRACK is "Y" ie yes 
            # and if flight_no != None which it will be if flight has not taken off at FLOGGER_AIRFIELD_NAME   
            #-----------------------------------------------------------------
            #
        #    dt = str(datetime.datetime.now())           # Get the datetime this track point is created as string
        #    sdt = dt[0:10] + "T" + dt[11:19] + "Z"      # Convert to string format for gpx, ie YYYY-MM-DDTHH:MM:SSZ   
        #    sdt = "%sT%sZ" % (dt[0:10],dt[11:19])      # Convert to string format for gpx, ie YYYY-MM-DDTHH:MM:SSZ
            
        
            if settings.FLOGGER_TRACKS == "Y" and flight_no != None:
                print "Flight_no is: ", flight_no
                print "Track point nos is: ", track_no
        #        dt = str(datetime.datetime.now())           # Get the datetime this track point is created as string
        #        sdt = dt[0:10] + "T" + dt[11:19] + "Z"      # Convert to string format for gpx, ie YYYY-MM-DDTHH:MM:SSZ   
        #        This print doesn't work as one of the values is of none-type, not sure why?
        #        print "Adding track data to: %i, %i, %f, %f, %f, %f %f " % (flight_no,track_no,latitude,longitude,altitude,course,speed)
                try:
                    cursor.execute('''INSERT INTO track(flight_no,track_no,latitude,longitude,altitude,course,speed,timeStamp) 
                        VALUES(:flight_no,:track_no,:latitude,:longitude,:altitude,:course,:speed,:timeStamp)''',                                           
                        {'flight_no':flight_no,'track_no':track_no,'latitude':latitude,'longitude':longitude,'altitude':altitude,'course':course,'speed':speed,'timeStamp':timeStamp})
                except:
                    print "Add trackpoint failed on insert: ignore trackpoint"
            else:
                print "Don't add track point"
            return
            
        def endTrack():
            return
        
        def CheckTrackData(cursor, flight_no, track_no, callsignKey):
        #    print "check flight_no if callsign in flight_no{}: ", flight_no, " Track_no is: ", track_no, " CallsignKey is: ", callsignKey 
            if flight_no.has_key(callsignKey) == 1:
                print "flight_no already has entry: ", callsignKey
            else:
                try:
                    cursor.execute('''SELECT max(id) FROM flight_log2 WHERE src_callsign =?''', (callsignKey,))
                except:
                    print "!!!ERROR - No record in flight_log2 for: ", callsignKey
                    # If this crashes need to think about adding record for flight_log2, but why?
                    exit()
                row_id = cursor.fetchone()[0]  # value of id for row just inserted use as flight_no for flight
                print "Last row ID of flight_log2 for callsign: ", callsignKey, " inserted was: ", row_id
                flight_no[src_callsign] = row_id
                track_no[callsignKey] = 1
                print "flight_no for callsignKey: ", callsignKey, " is: ", flight_no[callsignKey]
            return
        
        def check_position_packet (packet_str):  
            #    
            #-----------------------------------------------------------------
            # This function determines if airfield is in the list of APRS 
            # base stations used for receiving position fixes.
            #
            # base_list should be set up as part of the main code initialisation
            #-----------------------------------------------------------------
            #  
#            for base in APRS_base_list:
            for base in settings.FLOGGER_APRS_BASES:
                if string.find(str(packet_str), base) <> -1:
                    print "Found in list of APRS base stations: ", base
                    return base
            print "Not found base station in packet"
            return -1
        
        def delete_table (table): 
            #    
            #-----------------------------------------------------------------
            # This function deletes the SQLite3 table 
            # with the name supplied by "table".
            #-----------------------------------------------------------------
            #
#            print "delete_table. settings.FLOGGER_MODE: ", settings.FLOGGER_MODE
            if settings.FLOGGER_MODE == "test":
                print "Test only. Table %s not deleted" % (table)
                return
            parm = "DELETE FROM %s" % (table)
            try:
                cursor.execute(parm)
                print "New Delete %s table ok" % (table)
            except:
                print "New Delete %s table failed or no records in tables" % (table)      
            return
        
        def delete_flogger_file(folder, filename, days):
            #    
            #-----------------------------------------------------------------
            # This function deletes the files whose name contain filename in folder folder
            # if they were created up to and including the number of days in the past 
            # specified by the days parameter.
            # If days is zero then no deletions are performed
            # folder is the relative folder name
            # filename are the names of the files within folder
            #-----------------------------------------------------------------
            #
            print "folder: ", folder
            print "filename: ", filename
            if days <= 0:
                print "Don't delete old files, return"
                return
            
            now = time.time()
#            path = os.path.dirname(os.path.abspath(__file__))
            path = path_join_dd(os.path.dirname(__file__), [folder])
            print "path: ", path
#            if os.path.isdir(os.path.join(path, folder)):
            if os.path.isdir(path):
#            if os.path.isdir(path_join_dd(os.path.abspath(__file__), [folder])):
#                flist = os.listdir(folder)
#                flist = os.listdir(os.path.join(path, folder))
#                flist = os.listdir(path_join_dd(os.path.abspath(__file__), [folder]))
                flist = os.listdir(path)
            else:
                print "Not found: ", folder
                return
##            print "delete flist: ", flist
            for f in flist:
#                print "Pathname is: ", os.path.join(folder, f), " st_mtime is: ", os.stat(os.path.join(folder, f)).st_mtime
#                full_file = os.path.join(folder, f)
                full_file = os.path.join(path, f)
                file_find = string.find(full_file, filename) <> -1
                file_time = os.stat(full_file).st_mtime 
#                print "File_find is: ", file_find, ". File_time is: ", file_time, "Now is: ", now - days * 86400
                if (file_find == True) and (file_time <= (now - days * 86400)):
#                    print "Delete file: ", full_file
                    print "Full file_name file would be deleted now: ", full_name
#                    os.remove(full_file)
        #        else:
        #            print "File not deleted: %s" % full_file
            return
        
        def connect_APRS(sock):
            #    
            #-----------------------------------------------------------------
            #
            # This function tries to shutdown the specified sock and if it
            # fails closes it and then creates a new one and reconnects to the APRS system
            #    
            #-----------------------------------------------------------------
            #
            try:
                sock.shutdown(0)
            except socket.error, e:
                if 'not connected' in e:
                    print '*** Transport endpoint is not connected ***'
                print "socket no longer open so can't be closed, create new one"    
            else:
                print "Socket still open so close it"
                sock.close()
            print "Create new socket"
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((settings.APRS_SERVER_HOST, settings.APRS_SERVER_PORT))
            except Exception, e:
                print "Connection refused. Errno: ", e
                exit() 
            APRSparm = ('user %s pass %s vers %s %s filter r/%s/%s/%s\n ' % (settings.APRS_USER, 
                                                                             settings.APRS_PASSCODE, 
                                                                             settings.FLOGGER_NAME, 
                                                                             settings.FLOGGER_VER, 
                                                                             settings.FLOGGER_LATITUDE, 
                                                                             settings.FLOGGER_LONGITUDE, 
                                                                             settings.FLOGGER_RAD)) 
        #            print "APRSparm is: ", APRSparm      
        #            sock.send('user %s pass %s vers Python_Example 0.0.1 filter r/+54.228833/-1.209639/25\n ' % (settings.APRS_USER, settings.APRS_PASSCODE))
            sock.send(APRSparm)
            # Make the connection to the server
            sock_file = sock.makefile()
            return sock_file
                
            
        
        #    
        #----------------------------------------------------------------- 
        # Start of main code    
        #-----------------------------------------------------------------
        #
        

        print "FLOGGER_AIRFIELD_NAME from class is: " + settings.FLOGGER_AIRFIELD_NAME
#        path = os.path.dirname(os.path.abspath(__file__))
        settings.FLOGGER_BS = os.path.dirname(os.path.abspath(__file__)) 
        settings.FLOGGER_TRACKS_FOLDER = settings.FLOGGER_BS + "/tracks"      # Setup 'tracks' folder name - not defined in settings class anymore
        settings.FLOGGER_FLIGHTS_LOG = settings.FLOGGER_BS + "/flight_logs"
        
        
#        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
        print "path: ", path
#        tracks_folder = os.path.join(path, "tracks")
        tracks_folder = path_join(path, ["tracks"])
        print "tracks_folder: ", tracks_folder
        settings.FLOGGER_TRACKS_FOLDER = tracks_folder
#        flights_log = os.path.join(path, "logs")
        flights_log = path_join(path, ["logs"])
        print "flights_log: ", flights_log
        settings.FLOGGER_FLIGHTS_LOG = flights_log
        

        print "settings.FLOGGER_TRACKS_FOLDER: ", settings.FLOGGER_TRACKS_FOLDER
        #
        # User and passcode now mandatory positional parameters
        # Mode is an optional positional parameter, default is "live"
        #
#        try:
        parser = argparse.ArgumentParser()
#            parser.add_argument("--user", help="user and passcode must be supplied, see http://www.george-smart.co.uk/wiki/APRS_Callpass for how to obtain")
#            parser.add_argument("--passcode", help="user and passcode must be supplied", type=int)
#            parser.add_argument("--mode", help="mode is test or live, test modifies behaviour to add output for testing", default="test")
#            parser.add_argument('-s', '--smtp', help="URL of smtp server")
#            parser.add_argument('-t', '--tx', help="email address of sender")
#            parser.add_argument('-r', '--rx', help="email address of receiver")
#        except:
#            print "Parsing cmd line args failed"
            
        print "Cmd line args parsed"
        
        try:
            args = parser.parse_args()
            print "Cmd Line args parsed ok"
            #
            # Check parameters. If an smtp server address is specified then the sender and receiver email
            # addresses must also be supplied either in the call line or the config file
            #
            if (args.smtp == None and settings.FLOGGER_SMTP_SERVER_URL == ""):
                print "SMTP url not specified, don't send email"
            else:
                print "Set to send email"
                if (args.smtp <> None):
                    settings.FLOGGER_SMTP_SERVER_URL = args.smtp
                if (args.tx <> None):
                    settings.FLOGGER_SMTP_TX = args.tx
                if (args.rx <> None):
                    print "args.rx is: ", args.rx
                    settings.FLOGGER_SMTP_RX = args.rx
                elif ((args.tx == None or args.rx == None) and (settings.FLOGGER_SMTP_TX == "" or settings.FLOGGER_SMTP_RX == "")):
                    print "Email option parameters or config not valid. smtp=%s, SERVER_URL=%s, tx=%s, rx=%s, SMTP_TX=%s, SMTP_RX=%s" % \
                    (args.smtp, settings.FLOGGER_SMTP_SERVER_URL, args.tx, args.rx, settings.FLOGGER_SMTP_TX, settings.FLOGGER_SMTP_RX)
                    print "Exit"
                    exit()
                print "Email parameters are now: smtp=%s, SERVER_URL=%s, tx=%s, rx=%s, SMTP_TX=%s, SMTP_RX=%s" % \
                    (args.smtp, settings.FLOGGER_SMTP_SERVER_URL, args.tx, args.rx, settings.FLOGGER_SMTP_TX, settings.FLOGGER_SMTP_RX)           
            if (args.user <> None):
                settings.APRS_USER = args.user
            else:
                print "Taken from APRS_USER: ", settings.APRS_USER
            if args.passcode <> None:
                settings.APRS_PASSCODE = args.passcode
            else:
                print "Taken from form APRS_PASSCODE: ", settings.APRS_PASSCODE
            if args.mode <> None:
                print "Taken from args.mode: ", settings.FLOGGER_MODE 
                settings.FLOGGER_MODE = args.mode
            else:
                print "Taken from FLOGGER_MODE: ", settings.FLOGGER_MODE               
        except :
            print "Failed in command line arg parser"
#        print "user=", args.user, " passcode=", args.passcode, "mode=", args.mode, "smtp=", args.smtp, "tx=", args.tx, "rx=", args.rx
                
        # Creates or opens a file called flogger.sql3 as an SQLite3 DB
        
        #
        #-----------------------------------------------------------------
        # Build flogger db using schema
        # Delete SQLite3 database file if it already exists; stops it getting
        # too large during testing
        #-----------------------------------------------------------------
        #
        path = os.path.dirname(os.path.abspath(__file__))
#        schema_file = os.path.join(path,"../data/" + settings.FLOGGER_DB_SCHEMA)
        p1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
#        schema_file = os.path.join(path_join(p1, ["data"]),settings.FLOGGER_DB_SCHEMA)
        schema_file = path_join_dd(os.path.abspath(__file__), ["data", settings.FLOGGER_DB_SCHEMA])
        print "schema_file: ", schema_file
#        db_file = os.path.join(path,"../db/" + settings.FLOGGER_DB_NAME)       
#        db_file = os.path.join(path_join(p1,["db"]),settings.FLOGGER_DB_NAME)
        db_file = path_join_dd(os.path.abspath(__file__), ["db", settings.FLOGGER_DB_NAME])
        print "db_file: ", db_file

        
        
        if os.path.isfile(schema_file) and settings.FLOGGER_MODE <> "test":
            print "SQLite3 db file exists so delete it"
            os.remove(db_file)
        else:
            print "SQLite3 db file exists but in test mode so DON'T delete it!"
        
        db = sqlite3.connect(db_file)
        cursor = db.cursor()                            # Get a cursor object
        f = open(schema_file, 'rt')      # Open the db schema file for reading
        schema = f.read()                               
        cursor.executescript(schema)  
        print "End of building db: ", settings.FLOGGER_DB_NAME, " using schema: ", settings.FLOGGER_DB_SCHEMA
        
##        if os.path.isfile(settings.FLOGGER_DB_NAME):        
#        if os.path.isfile(settings.FLOGGER_DB_NAME) and settings.FLOGGER_MODE <> "test":
#            print "SQLite3 db file exists so delete it"
#            os.remove(settings.FLOGGER_DB_NAME)
#        else:
#            print "SQLite3 db file exists but in test mode so DON'T delete it!"
#        
#        db = sqlite3.connect(settings.FLOGGER_DB_NAME)
#        cursor = db.cursor()                            # Get a cursor object
##        f = open(settings.FLOGGER_DB_SCHEMA, 'rt')      # Open the db schema file for reading
#        f = open(settings.FLOGGER_DB_SCHEMA, 'rt')      # Open the db schema file for reading
#        schema = f.read()                               
#        cursor.executescript(schema)                                
##      cursor.executescript(schema)                ###   # Build flogger db from schema
#        print "End of building db: ", settings.FLOGGER_DB_NAME, " using schema: ", settings.FLOGGER_DB_SCHEMA
        
        #    
        #-----------------------------------------------------------------
        # Build local database from flarmnet of aircraft    
        #-----------------------------------------------------------------
        #
        
        if flarmdb(settings.FLOGGER_FLARMNET_DB_URL, cursor, db, "flarm_data", settings) == True:
            print "Flarmnet db built"   
        else:
            print "Flarmnet db build failed, exit" 
            exit()
        
        #    
        #-----------------------------------------------------------------
        # Determine location details, latitude, longitude and elevation
        #-----------------------------------------------------------------
        #
        
        if settings.FLOGGER_AIRFIELD_DETAILS <> "":
            loc = get_coords(settings.FLOGGER_AIRFIELD_DETAILS)
            i = 1
            while loc == False and i<=100:
#            while loc[2] == None:
#                print "get_coords returned loc[2] as None, retry", " Retry count get_coords: ", i
                print "get_coords returned False, retry", " Retry count get_coords: ", i
                loc = get_coords(settings.FLOGGER_AIRFIELD_DETAILS)
                i = i + 1
#                time.sleep (1)
                
            if loc == False:
                if settings.FLOGGER_LATITUDE <> "" and settings.FLOGGER_LONGITUDE <> "" and settings.FLOGGER_QNH >=0 :
                    print "Geolocator failed use values from settings"
                else:
                    print "Geoloactor failed and no value for lat, long, QNH. Run again, might work"
                    exit(2)
            else:
                settings.FLOGGER_LATITUDE       = str(loc[0])   # Held as string
                settings.FLOGGER_LONGITUDE      = str(loc[1])   # Held as string
                settings.FLOGGER_QNH            = loc[2]        # Held as number
                if settings.FLOGGER_QNH == None:
                    print "Probable Geolocator error, set FLOGGER_QNH default 0, loc[2]: ", loc[2]
                    settings.FLOGGER_QNH = 0
                    exit(3)
                print "Location is: ", settings.FLOGGER_AIRFIELD_DETAILS, " latitude: ", loc[0], " longitude: ", loc[1], " elevation: ", loc[2] 
#                print "Location is: ", settings.FLOGGER_AIRFIELD_DETAILS, " latitude: ", settings.FLOGGER_LATITUDE , \
#                                    " longitude: ", settings.FLOGGER_LONGITUDE, " elevation: ", settings.FLOGGER_QNH       
        else:
            print "Use location data from settings"   
            
        #    
        #-----------------------------------------------------------------
        # Set up list of APRS base stations to be used
        # (Note this code could be nicer but will do for now)
        #-----------------------------------------------------------------
        #    
            
        #APRS_base_list = [settings.FLOGGER_APRS_BASE_1, 
        #                  settings.FLOGGER_APRS_BASE_2, 
        #                  settings.FLOGGER_APRS_BASE_3,
        #                  settings.FLOGGER_APRS_BASE_4,] 
        
#        APRS_base_list = settings.FLOGGER_APRS_BASES 
        
        #    
        #-----------------------------------------------------------------
        # Initialise API for computing sunrise and sunset    
        #-----------------------------------------------------------------
        #
        
        location = ephem.Observer()
        location.pressure = 0
        #location.horizon = '-0:34'    # Adjustments for angle to horizon
        location.horizon = settings.FLOGGER_LOCATION_HORIZON    # Adjustments for angle to horizon
        
        location.lat = settings.FLOGGER_LATITUDE
        location.lon = settings.FLOGGER_LONGITUDE
        
        print "Location for ephem is: ", settings.FLOGGER_AIRFIELD_DETAILS, " latitude: ", location.lat, " longitude: ", location.lon, " elevation: ", settings.FLOGGER_QNH   
        
        date = datetime.datetime.now()
        next_sunrise = location.next_rising(ephem.Sun(), date)
        next_sunset = location.next_setting(ephem.Sun(), date)
        print "Sunrise today: ", date, " is: ", next_sunrise
        print "Sunset today: ", date, " is: ", next_sunset
            
        #    
        #-----------------------------------------------------------------
        # Make the connection to the APRS server
        #-----------------------------------------------------------------
        #
            
        start_time = datetime.datetime.now()
        keepalive_time = time.time()
        #sock_file = sock.makefile()
        print "Start time!" 
        sock = APRS_connect(settings)
        sock_file = sock.makefile()
#        print "libfap_init"
#        rtn = libfap.fap_init()
#        if rtn <> 0:
#            print "Failed to connect to APRS, check parameters"
#            exit()
#        print "Libfap return: ", rtn
        
        #    
        #-----------------------------------------------------------------
        # Set up paths for data, logs and tracks 
        #-----------------------------------------------------------------
        #
        
        SB_DATA = "SB_data" + str(start_time)
        SB_Log = "SB_Log" + str(start_time)
        SB_DATA = str(SB_DATA).replace(" ","_")
        SB_Log = str(SB_Log).replace(" ","_")
        SB_DATA = str(SB_DATA).replace(":","-")
        SB_Log = str(SB_Log).replace(":","-")
        print "Checking log paths: ", settings.FLOGGER_LOG_PATH
        if settings.FLOGGER_LOG_PATH <> "":
            if not os.path.isdir(settings.FLOGGER_LOG_PATH):
                print "Log path is not directory", 
                SB_DATA = os.path.abspath(settings.FLOGGER_LOG_PATH) + "/" + SB_DATA
                SB_Log  = os.path.abspath(settings.FLOGGER_LOG_PATH) + "/" + SB_Log
                try:
                    #print "Creating log folder"
                    os.makedirs(settings.FLOGGER_LOG_PATH)
                    print "Created: ", settings.FLOGGER_LOG_PATH
                except:
                    print "FLOGGER_LOG_PATH does not exist. Please check settings."
                    exit()    
        print "SB data file is: ", SB_DATA
        print "SB log file is: ", SB_Log
        
        #sys.stdout = open(SB_Log, 'w')
        #print "Datafile open"
        test = False
        if test == True:
            datafile = open (SB_DATA, 'rw')
            print "In test mode"
        else:
            datafile = open (SB_DATA, 'w')
            print "In live mode"
            
        #    
        #-----------------------------------------------------------------
        # Setup cntrl-c handler
        # 
        #-----------------------------------------------------------------
        #
        
#        print "Setup cntrl-c handler"
#        sig_handler(db, cursor)
        #time.sleep(5) # Press Ctrl+c here            # Just for testing
        
        #    
        #-----------------------------------------------------------------
        # Main loop reading data from APRS server and processing records
        # This continues until sunset after which the data recorded is processed
        #-----------------------------------------------------------------
        #
        
        i = 0
        try:
#            while 1:
            while settings.FLOGGER_RUN:
                print "FLOGGER_RUN: ", settings.FLOGGER_RUN
        #     for i in range(1000000):
                i = i + 1
                datetime_now = datetime.datetime.now()
                previous_sunrise = location.previous_rising(ephem.Sun(), date).datetime()
                next_sunrise = location.next_rising(ephem.Sun(), date).datetime()
                previous_sunset = location.previous_setting(ephem.Sun(), date).datetime()
                next_sunset = location.next_setting(ephem.Sun(), date).datetime()
                # Set datetime to current time + FLOGGER_LOG_TIME_DELTA to start processing flight log 
                # that number of hours before sunset
                log_datetime = datetime.datetime.now() + datetime.timedelta(hours=settings.FLOGGER_LOG_TIME_DELTA)
        #        print "Log datetime is: ", log_datetime
                location.date = ephem.Date(log_datetime)
                print "Ephem date is: ", location.date
                s = ephem.Sun()
                s.compute(location)
                twilight = -6 * ephem.degree    # Defn of Twilight is: Centre of Sun is 6, 12, 18 degrees below horizon (civil, nautical, astronomical)  
#               daylight = s.alt > twilight
#                print "Just for testing aprs_parse"
#                daylight = True
#                if daylight:
                if s.alt > twilight:
                    print "Is it light at Location? Yes", location, " Ephem date is: ", ephem.Date(location.date), " Next sunset at: ", location.next_setting(ephem.Sun())
                else:
                    print "Is it light at Location? No", location, " Ephem date is: ", ephem.Date(location.date), " Next sunrise at: ", location.next_rising(ephem.Sun())
                    process_log(cursor,db, settings)
        
        #
        # Dump tracks from flights table as .gpx
        # This updates each flight in flights table with trackfile name
        #
                    print "Dump tracks"
                    dump_tracks2(cursor, db, settings)
                    dump_IGC(cursor, db, settings)
                    
        #
        # Experimental. Find tug used for each launch
        #
                    find_tug(cursor, db, settings)
                    print "Find tug phase end"
                        
                    
        #
        # Dump flights table as cvs file
        # If no flights then returns ""
        #
                    print "Dump flights table"
                    csv_file = dump_flights(settings)
        #
        # Email flights csv file if required
        # email_log2 sorts out if there are no flights on any one day
        # FLOGGER_SMTP_SERVER_TX is either set in config by user or value taken from cmd line --smtp parm.
        # 
                    if settings.FLOGGER_SMTP_SERVER_URL <> "":
                        print "Email today's flight log. RX: " + settings.FLOGGER_SMTP_RX
                        email_log2(settings.FLOGGER_SMTP_TX, settings.FLOGGER_SMTP_RX, csv_file, datetime.date.today(), settings)
                    else:
                        print "Don't email flight log, no flights"
                    
        #            
        # Delete entries from daily flight logging tables etc
        #
                    
                    delete_table("flight_log")
                    delete_table("flight_log2")
                    delete_table("flight_log_final")
                    delete_table("flight_group")
##DEL                    delete_table("flights")
                    delete_table("track")
                    delete_table("trackFinal")
                    delete_table("flarm_db")        # flarm_db should be rebuilt at start of each day
                    db.commit()
                    # Wait for sunrise
        #            wait_time = next_sunrise - datetime_now
                        
                    datetime_now = datetime.datetime.now()
                    date = datetime.datetime.now()
                    location.date = ephem.Date(datetime.datetime.now())
                    next_sunrise = location.next_rising(ephem.Sun(), date).datetime()
                    
                    print "Location Date now: ", location.date, " Next sunrise is: ", next_sunrise
                    wait_time = location.next_rising(ephem.Sun(), date).datetime() - datetime_now
                    print "Next sunrise at: ", location.next_rising(ephem.Sun(), date).datetime(), " Datetime now is: ", datetime_now
                    # Wait an additional 2 hours (in seconds) more before resuming. 
                    # Just a bit of security, not an issue as unlikely to start flying so early
                    wait_time_secs = int(wait_time.total_seconds()) + (2 * 60 * 60) 
                    # close socket -- not needed. Create new one at sunrise
                    try:
                        sock.shutdown(0)
                    except socket.error as msg:
                        print "Socket failed to shutdown, ignore. Msg is: " , msg
                    sock.close() 
        #
        # Delete historic files as specified
        #            
                    print "+++++++Phase 4 Start Delete out of date files+++++++" 
                    delete_flogger_file(settings.FLOGGER_TRACKS_FOLDER, "track", settings.FLOGGER_DATA_RETENTION)
                    delete_flogger_file(settings.FLOGGER_FLIGHTS_LOG, "flights.csv", settings.FLOGGER_DATA_RETENTION)
                    print "-------Phase 4 End-------" 
                    
        #
        # Sleep till sunrise
        # Then open new socket, set ephem date to new day
        #
                    print "Wait till after sunrise at: ", next_sunrise, " Elapsed time: ", wait_time, ". Wait seconds: ", wait_time_secs
#                    self.RunningLabel.setText("Sleeping")
                    time.sleep(wait_time_secs)
                    # Sun has now risen so recommence logging flights
                    location.date = ephem.Date(datetime.datetime.now())
                    print "Woken up. Date time is now: ", datetime.datetime.now()
                    print "Ephem datetime on wakeup is: ", ephem.Date(location.date)
                    # Make new socket as old one will have timed out during the 'big' sleep, reset the timers
                    start_time = datetime.datetime.now()
                    keepalive_time = time.time()
                    sock = APRS_connect(settings)
                    sock_file = sock.makefile()         # Note both sock & sock_file get used
                    #    
                    #-----------------------------------------------------------------
                    # Build local database from flarmnet of aircraft for today
                    # Note source flarm_db may have changed during previous day 
                    #-----------------------------------------------------------------
                    #
                    if flarmdb(settings.FLOGGER_FLARMNET_DB_URL, cursor, db, "flarm_data", settings) == True:
                        print "Flarmnet db built for today"   
                    else:
                        print "Flarmnet db re-build failed, exit" 
                        exit()
                    i = 0                               # Count of todays APRS reads reset   
                    flight_no = {}                      # Re-initialise flight_no dictionary at start of day
                    track_no = {}                       # Re-initialise track_no dictionary at start of day
                    continue
                            
                current_time = time.time()
                elapsed_time = int(current_time - keepalive_time)
                print "Elapsed time is: ", elapsed_time
                if (current_time - keepalive_time) > settings.FLOGGER_KEEPALIVE_TIME:
                    try:
                        print "Socket open for: ", (current_time - keepalive_time), " seconds, send keepalive"
                        rtn = sock_file.write("#Python Example App\n\n")
                        sock_file.flush()  # Make sure it gets sent
                        print "Send keepalive", elapsed_time, " rtn is: ", rtn
                        keepalive_time = current_time
                    except Exception, e:
                        print ('something\'s wrong with socket write. Exception type is %s' % (`e`))
                        sock_file = connect_APRS(sock) 
                        print "New connection to APRS made"
                        continue
                else:
                    print "No keepalive sent"
                        
                print "In while loop. Count= ", i
                try:
                    if test == False:
                        # In live mode so use socket read
                        print "Read socket"
                        packet_str = sock_file.readline()
#                        print "Raw APRS Packet: ", packet_str
        #                datafile.write(packet_str)
                    else:
                        # In test mode so file read
                        packet_str = datafile.readline()
                except socket.error:
                    print "Socket error on readline"
                    
#                print "packet string length is: ", len(packet_str), " packet is: ", packet_str
                try:
                    len_packet_str = len(packet_str)
                except TypeError:
                    packet_str_hex = ":".join("{:02x}".format(ord(c)) for c in packet_str)
                    len_packet_str = len(packet_str_hex) / 3
                    print "TypeError on packet_str length. Now is: ", len_packet_str
                
                if len_packet_str == 0:
                    # create new socket & connect to server
                    print "Read returns zero length string on iteration: ", i
                    # Wait 20 seconds
                    time.sleep(20)
        #            continue
                    try:
                        sock.shutdown(0)
                    except socket.error, e:
                        if 'not connected' in e:
                            print '*** Transport endpoint is not connected ***'
                        print "socket no longer open so can't be closed, create new one"    
                    else:
                        print "Socket still open so close it"
                        sock.close()
                    print "Create new socket"
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        sock.connect((settings.APRS_SERVER_HOST, settings.APRS_SERVER_PORT))
                    except Exception, e:
                        print "Connection refused. Errno: ", e
                        exit() 
                    APRSparm = ('user %s pass %s vers %s %s filter r/%s/%s/%s\n ' % (settings.APRS_USER, 
                                                                                     settings.APRS_PASSCODE, 
                                                                                     settings.FLOGGER_NAME, 
                                                                                     settings.FLOGGER_VER, 
                                                                                     settings.FLOGGER_LATITUDE, 
                                                                                     settings.FLOGGER_LONGITUDE, 
                                                                                     settings.FLOGGER_RAD)) 
        #            print "APRSparm is: ", APRSparm      
        #            sock.send('user %s pass %s vers Python_Example 0.0.1 filter r/+54.228833/-1.209639/25\n ' % (settings.APRS_USER, settings.APRS_PASSCODE))
                    sock.send(APRSparm)
                    # Make the connection to the server
                    sock_file = sock.makefile()
        # Delete following line when not running in test mode
        #            exit()
                    continue
                #
                # Parse the returned packet into fields
                # Note this uses a modified version of libfap as the master on
                # github contains an error
                #
                packet = aprs_parse(packet_str, settings)
                if packet:
                    print "aprs_parse rtnd: ", packet
                else:
                    print "aprs_parse Failed. Not glider position packet"
                    continue
                src_callsign = packet["from"]
                latitude = packet["latitude"]
                longitude = packet["longitude"]
                altitude = packet["altitude"]
                speed = packet["speed"]
                course = packet["course"]
                timestamp = packet["timestamp"]
                CheckVals(src_callsign, "latitude", latitude)
                nvalues[src_callsign]["longitude"] = longitude
                nvalues[src_callsign]["altitude"] = altitude 
                nvalues[src_callsign]["speed"] = speed   
                #
                # Removed libfap parsing 20180424
                # 
                
                # Check if callsign is in the fleet 
                if fleet_check_new(str(src_callsign)) == False:
                    print "Aircraft ", src_callsign, " not registered at ", settings.FLOGGER_AIRFIELD_NAME, " , ignore"
                    print "-----------------End of Packet: ", i, " ------------------------------"
                    continue
                else:
                    print "Aircraft ", src_callsign, " is in ", settings.FLOGGER_AIRFIELD_NAME, " fleet, process"
                    # Use registration if it is in aircraft table else just use Flarm_ID
        #            src_callsign =     callsign_trans(src_callsign)
        #            print "Aircraft callsign is now: ", src_callsign
                    registration =     callsign_trans(src_callsign)
                    print "Aircraft registration is: ", registration, " FLARM code is: ", src_callsign
                    # Check with this aircraft callsign has been seen before
                    CheckPrev(src_callsign, 'latitude', 0)
                    CheckVals(src_callsign, 'latitude', 0)
                    # Current and previous data values created
                    local_time = datetime.datetime.now()
                    fl_date_time = local_time.strftime("%D:%H:%M:%S")
                    fl_date = local_time.strftime("%y/%m/%d")
        #             fl_date = local_time.strftime("%D")
                    fl_time = local_time.strftime("%H:%M:%S")
                    print "src_callsign matched: ", src_callsign, " ", fl_date_time, " Latitude is: ", latitude
        #             print "Line ", i, " ", packet[0].orig_packet
                    
        #            if nprev_vals[src_callsign]['speed'] == 0 and nvalues[src_callsign]['speed'] <> 0:
        #            af_loc = (settings.FLOGGER_LATITUDE, settings.FLOGGER_LONGITUDE)
        #            takeoff_loc = (latitude, longitude)
                    takeoff_dist = vincenty((settings.FLOGGER_LATITUDE, settings.FLOGGER_LONGITUDE), (latitude, longitude)).meters
                    print "Test for was stopped now moving. nprevs[speed] is: " + str(nprev_vals[src_callsign]['speed']) + " nvalues[speed] is: "+ str(nvalues[src_callsign]['speed'])
        #            if nprev_vals[src_callsign]['speed'] <= V_SMALL and nvalues[src_callsign]['speed'] > V_SMALL:
        #            if nprev_vals[src_callsign]['speed'] <= V_SMALL and nvalues[src_callsign]['speed'] > V_SMALL and takeoff_dist < settings.FLOGGER_AIRFIELD_LIMIT:
                    if nprev_vals[src_callsign]['speed'] <= V_SMALL and nvalues[src_callsign]['speed'] > V_TAKEOFF_MIN and takeoff_dist < settings.FLOGGER_AIRFIELD_LIMIT:
        
                        # The previous speed means it was probably stopped, the current speed means it is probably moving and the position is within the airfield
                    # Following test for case when Flarm is switched on for first time when stationary and at an
                    # altitude greater than settings.FLOGGER_QNH, ie a special case of initial location. nprev_vals get set to zero when aircraft
                    # first detected by flarm. Doesn't work.  Needs thought
        #            if (nprev_vals[src_callsign]['speed'] <= V_SMALL and nvalues[src_callsign]['speed'] > V_SMALL) or (nprev_vals[src_callsign]['speed'] == nvalues[src_callsign]['speed'] and  nvalues[src_callsign]['speed']> V_SMALL):
                        print "New test true for switch-on"
                        print "Takeoff point is: ", (latitude, longitude), "Distance is: ", takeoff_dist
                        email_msg(settings.FLOGGER_SMTP_TX, settings.FLOGGER_SMTP_RX, registration, fl_time, settings)
                        # aircraft was stopped, now isn't
                        # Enhancement.  At this point create new Track table record for the flight.
                        # Set track_no to current value and increment for use by next new flight.
                        # Flight_no (ie flight_log2 id field) has to copied to the Track table record
                        # each time new track data record for the flight is added.
                        print "Aircraft ", src_callsign, " was stopped, now moving. Create new record"    
                        cursor.execute('''INSERT INTO flight_log2(sdate, stime, edate, etime, duration, src_callsign, max_altitude, speed, registration)
                                    VALUES(:sdate,:stime,:edate,:etime,:duration,:src_callsign,:max_altitude,:speed, :registration)''',
                                    {'sdate':fl_date, 'stime':fl_time, 'edate': "", 'etime':"", 'duration': "", 'src_callsign':src_callsign, 'max_altitude':altitude, 'speed':0, 'registration': registration})
                        nprev_vals[src_callsign]['speed'] = nvalues[src_callsign]['speed']
                        
                        print "Storing initial track data"
                        cursor.execute('''SELECT max(id) FROM flight_log2''')
                        lastrow_id = cursor.fetchone()[0]  # value of id for row just inserted use as flight_no for flight
                        print "Last row ID of flight_log2 inserted was: ", lastrow_id
                        flight_no[src_callsign] = lastrow_id
        #                flight_no[src_callsign] = cursor.lastrowid    # Unique value of row just created
                        track_no[src_callsign] = 1                      # Initialise trackpoint number for this flight
                        addTrack(cursor, flight_no[src_callsign],track_no[src_callsign],longitude,latitude,altitude,course,speed,timestamp)
                        track_no[src_callsign] += 1                     # Increment trackpoint number for this flight
                        
        #            if nprev_vals[src_callsign]['speed'] <> 0 and nvalues[src_callsign]['speed'] == 0:
        #            print "Test for was moving is now stopped"
                    print "Test for was moving is now stopped. nprev=: ", nprev_vals[src_callsign]['speed'], " nval=: ", nvalues[src_callsign]['speed'], " V_LANDING_MIN=: ", V_LANDING_MIN
        #            if nprev_vals[src_callsign]['speed'] > V_SMALL and nvalues[src_callsign]['speed'] <= V_SMALL:
                    if nprev_vals[src_callsign]['speed'] > V_LANDING_MIN and nvalues[src_callsign]['speed'] <= V_LANDING_MIN:
                        # aircraft was moving is now stopped
                        print "Aircraft ", src_callsign, " was moving, now stopped. Update record for end date & time"
                        # Add final track record
                        try:
                            addTrack(cursor, flight_no[src_callsign],track_no[src_callsign],longitude,latitude,altitude,course,speed,timestamp)
                            # Find latest record for this callsign
                        except KeyError, reason:
                            print "addTrack failed. Trackpoint ignored. Reason: ", reason
        #
        # Bug 20150520-1 Test Start
        #                
                        try:
                            cursor.execute('''SELECT max(id) FROM flight_log2 WHERE src_callsign =?''', (src_callsign,))
                            r = cursor.fetchone()
                            try:
                                rowid = r[0]
                                cursor.execute('''SELECT sdate, stime, max_altitude FROM flight_log2 WHERE ROWID =?''', (rowid,))
                                row = cursor.fetchone()
                                print "Test Bug 20150520-1 ok, row is: ", row
                            except:
                                print "Select for sdate/stime failed for: ", rowid
                        except:
                            print "Select max(id) failed for: ", src_callsign
        #
        # Bug 20150520-1 Test End
        #
                            
                        cursor.execute('''SELECT sdate, stime, max_altitude, id FROM flight_log2 WHERE 
                                        ROWID IN (SELECT max(id) FROM flight_log2 WHERE src_callsign =? )''', (src_callsign,))
                        row = cursor.fetchone()
        #
        # Bug 20150520-1 Start
        # Re-initialise altitude for stopped aircraft to zero. And above row is None
        #
                        if row == None:
                            print "Bug 20150520-1. We have a problem with: ", src_callsign
                            continue
        #
        # Bug 20150520-1 End
        #
                        
        #                for r in row:
        #                    print "Returned row for callsign: ", src_callsign, " is: ", r
        #                 end_time = datetime.strptime(fl_time,'%H:%M:%S') 
                        end_time = datetime.datetime.now()  # In seconds since epoch
                        start_date = row[0]  # In %y/%m/%d format
                        start_time = row[1]  # In %H:%M:%S format
                        max_altitude = row[2]
                        flight = row[3]      # id field of flight_log2
                        
                        fl_end_datetime = datetime.datetime.now()
                        fl_end_date = fl_end_datetime.strftime("%y/%m/%d")
                        fl_end_time_str = fl_end_datetime.strftime("%H:%M:%S")
        #                fl_end_time = fl_end_time_str
                        fl_end_time = datetime.datetime.strptime(fl_end_time_str, "%H:%M:%S")
                        print "Flight End date and time are: ", fl_end_date, " , ", fl_end_time_str
                        print "Flight Start date and time are: ", start_date, " , ", start_time
        
                        fl_start_time = datetime.datetime.strptime(start_time, "%H:%M:%S")  # Convert flight start time to type time
                        fl_duration_datetime = fl_end_time - fl_start_time  # fl_duration_time is a string format %H:%M:%S
        #                fl_duration_time = datetime.datetime.strptime(fl_duration_datetime, "%H:%M:%S")
                        c = fl_duration_datetime
        #                fl_duration_time = "%.2dh: %.2dm: %.2ds" % (c.seconds//3600,(c.seconds//60)%60, c.seconds%60)
                        fl_duration_time = "%.2d: %.2d: %.2d" % (c.seconds//3600,(c.seconds//60)%60, c.seconds%60)
                        fl_duration_time_str = str(fl_duration_time)
                        print "Start time: ", fl_start_time, "End time: ", fl_end_time_str, "Duration: ", fl_duration_time, " Max altitude: ", max_altitude
                        # Add record to flight_log_final
                        cursor.execute('''INSERT INTO flight_log_final(sdate, stime, edate, etime, duration, src_callsign, max_altitude, speed, registration, flight_no)
                                    VALUES(:sdate,:stime,:edate,:etime,:duration,:src_callsign,:max_altitude,:speed, :registration,:flight_no)''',
                                    {'sdate':start_date, 'stime':start_time, 'edate': fl_end_date, 'etime':fl_end_time_str,
                                    'duration': fl_duration_time_str, 'src_callsign':src_callsign, 'max_altitude':max_altitude, 'speed':0, 'registration': registration, 'flight_no': flight})
                        print "Updated flight_log_final", src_callsign
        #                flogger_landout_check(flight_reg, af_centre, radius, landing_coords, mode)
                        af_loc = (settings.FLOGGER_LATITUDE, settings.FLOGGER_LONGITUDE)
                        cursor.execute('''SELECT land_out FROM flight_log_final WHERE flight_no=?''', (flight,))
                        row = cursor.fetchone()
                        if row[0] == None:
                            # Check whether land_out already been logged
                            # This is needed since using input from multiple base stations, landout can be logged more than once 
                            res =landout_check(registration, flight, af_loc, settings.FLOGGER_AIRFIELD_LIMIT, (latitude, longitude), settings.FLOGGER_LANDOUT_MODE, settings)
                            print "Landout check is: ", res
                            if res == True:  
                                landout_status = "yes"
                            else:
                                landout_status = "no"
                            cursor.execute('''UPDATE flight_log_final SET land_out=? WHERE flight_no=?''', (landout_status,flight))
                        else:
                            print "Landout check. row[0]: ", row[0]
                        # Update flight record in flight_log2
                        cursor.execute(''' SELECT max(id) FROM flight_log2 WHERE src_callsign =?''', (src_callsign,))
                        row = cursor.fetchone()
                        rowid = row[0]
                        print "Update row: ", rowid
                        try:
                            cursor.execute('''UPDATE flight_log2 SET edate=?, etime=?, duration=?, max_altitude=?, speed=? WHERE ROWID=?''',
                                        (fl_end_date, fl_end_time_str, fl_duration_time_str, max_altitude, 0, rowid))
                            print "Updated flight_log2", src_callsign, " Row: ", rowid
                        except:
                            print "Failed to update flight_log2: ", src_callsign, " Row: ", rowid
                        nprev_vals[src_callsign]['speed'] = nvalues[src_callsign]['speed']  # ie set to '0'
        #
        # Bug 20150520-1
        # Re-initialise altitude for stopped aircraft to zero
        #
                        print "Bug 20150520-1. Re-initialise altitude in nvalues & nprev_vals for: ", src_callsign
                        nprev_vals[src_callsign]['altitude'] = 0
                        nvalues[src_callsign]['altitude'] = 0 
                        
                        # Check updated record
                        print "Check fields in flight_log2: ", src_callsign, " Row: ", rowid
                        cursor.execute('''SELECT ROWID, sdate, stime, edate, etime, duration, max_altitude FROM flight_log2 WHERE 
                                        ROWID IN (SELECT max(id) FROM flight_log2 WHERE src_callsign =? )''', (src_callsign,))
                        
                        row = cursor.fetchone()
                        for r in row:
                            print "Returned row for callsign: ", src_callsign, " is: ", r
                            
                        db.commit()    
                        print "-----------------End of Packet: ", i, " ------------------------------"
                        continue
        #            if nprev_vals[src_callsign]['speed'] == 0 and nvalues[src_callsign]['speed'] == 0:
                    print "Is Aircraft %s moving? nprev.speed=%d, nvalues.speed=%d, nvalues.altitude=%d" % (src_callsign, nprev_vals[src_callsign]['speed'], nvalues[src_callsign]['speed'], nvalues[src_callsign]['altitude'])        
        #            if nprev_vals[src_callsign]['speed'] <= V_SMALL and nvalues[src_callsign]['speed'] <= V_SMALL and nvalues[src_callsign]['altitude'] <= settings.FLOGGER_QNH:
                    if nprev_vals[src_callsign]['speed'] <= V_TAKEOFF_MIN and nvalues[src_callsign]['speed'] <= V_TAKEOFF_MIN and nvalues[src_callsign]['altitude'] <= settings.FLOGGER_QNH:
                        # Aircraft hasn't moved and is not at an altitude greater than Sutton Bank.  
                        print "Aircraft: ", src_callsign, " Not moving. Speed was: ", nprev_vals[src_callsign]['speed'], " Speed is: ", nvalues[src_callsign]['speed']
                    else:
                        # aircraft is moving. Check whether current altitude is greater than previous
                        # Enhancement. Add new record to Tracks table for this flight here. Track_no for flight is initialised
                        # when flight record is created, initial Track table record for flight is also created at that time
                        print "Aircraft ", src_callsign, " is still moving"
                        # Check whether a track list has been set up.  May have to add flight_log2 record as well??
                        CheckTrackData(cursor, flight_no, track_no, src_callsign)
                        print "Flight details are: ", flight_no[src_callsign]
                        # Add track record for moving aircraft
                        addTrack(cursor, flight_no[src_callsign],track_no[src_callsign],longitude,latitude,altitude,course,speed,timestamp)
                        track_no[src_callsign] += 1                 # Next trackpoint number for this flight
                        print "Old height was: ", nprev_vals[src_callsign]['altitude'], " New height is: ", nvalues[src_callsign]['altitude']
                        if nvalues[src_callsign]['altitude'] > nprev_vals[src_callsign]['altitude']:
                            print "Aircraft ", src_callsign, " is now higher than max height, was: ", nprev_vals[src_callsign]['altitude'], " now: ", nvalues[src_callsign]['altitude']
                            cursor.execute('''UPDATE flight_log2 SET max_altitude=? WHERE src_callsign=? ''', (altitude, src_callsign))
                            nprev_vals[src_callsign]['altitude'] = nvalues[src_callsign]['altitude']  # Now higher
                        else:
                            print "Aircraft callsign: ", src_callsign, " is moving but is not higher than max height: ", nvalues[src_callsign]['altitude'], " Speed is: ", nvalues[src_callsign]['speed'], " Was: ", nprev_vals[src_callsign]['speed']
                            # Set previous speed values to current
                            nprev_vals[src_callsign]['speed'] = nvalues[src_callsign]['speed']
                            continue
                        
                    print "Values for callsign Commit: ", src_callsign, " Values are: ", nvalues[src_callsign], " Prev_vals are: ", nprev_vals[src_callsign]
                    db.commit()        
                print "-----------------End of Packet: ", i, " ------------------------------"
#            libfap.fap_free(packet)
                    
        except KeyboardInterrupt:
            print "Keyboard input received, ignore"
        #    db.commit()
            pass
        
#        print "libfap_cleanup. If not called results in memory leak"
#        libfap.fap_cleanup()
        # close socket -- must be closed to avoid buffer overflow
        sock.shutdown(0)
        sock.close()
        # Close the database. Note this should be on all forms of exit
        db.close()
