#
#-----------------------------------------------------------------
# Function to find whether a flight was launched by tug (tow plane).
# If yes then add tug registration an height at which glider was released
# 
# Note tug flights have to be recorded to determine this, ie setting.FLOGGER_LOG_TUGS = 'Y'
# 
#-----------------------------------------------------------------
#

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
from flogger_test_YorN import test_YorN

def find_tug(cursor, db, settings):
    #
    # Finds if a tug launched a glider and if yes puts tug registration in flights table for 
    # the glider flight
    #
    def glider_fleet_check(registration, setttings):
        #
        # Checks if registration is in fleet list if fleet checking is being used or
        # checks that registration is a glider if fleet checking is not being used
        #
        try: 
            if settings.FLOGGER_FLEET_LIST[registration] > 200 and settings.FLOGGER_FLEET_LIST[registration] < 300 :
                # It's a Motor Glider in our fleet, ie not a glider
                return False
            else:
                if settings.FLOGGER_FLEET_LIST[registration] <= 100:    # Gliders are 0-99
                    return True
        except KeyError: 
#            print "Not in local fleet: ", registration
            # It's not a Motor Glider in specified fleet   
#            if settings.FLOGGER_FLEET_CHECK == "N" or settings.FLOGGER_FLEET_CHECK == "n":  
            if not test_YorN(settings.FLOGGER_FLEET_CHECK):
                        cursor.execute('''SELECT aircraft_type FROM flarm_db WHERE registration=?''', (registration,))
                        aircraft_type = cursor.fetchone()
    #                    print "Glider Fleet check. Registration: ", registration, " Type: ",  aircraft_type[0]
                        if int(aircraft_type[0]) == 1:
                            return True
        return False
    
    def tug_fleet_check(registration, settings):
        #
        # Checks if registration is tug in fleet list if fleet checking is being used or
        # checks that registration is a tug ("plane" or "ultralight") if fleet checking is not being used
        #
#        if settings.FLOGGER_FLEET_CHECK == "N" or settings.FLOGGER_FLEET_CHECK == "n": 
        if not test_YorN(settings.FLOGGER_FLEET_CHECK):
                    cursor.execute('''SELECT aircraft_type FROM flarm_db WHERE registration=?''', (registration,))
                    aircraft_type = cursor.fetchone()
#                    print "Tug Fleet check. Registration: ", registration, " Type: ",  aircraft_type[0]
                    if int(aircraft_type[0]) == 2 or int(aircraft_type[0]) == 3 :
                        return True
        else:
            if settings.FLOGGER_FLEET_LIST[registration] > 100 and settings.FLOGGER_FLEET_LIST[registration] < 200 :
                return True
        return False
            
    print "find_tug called"
    cursor.execute('''SELECT id, stime, duration, registration, max_altitude FROM flights ORDER by stime''')
    rows = cursor.fetchall()
    for row in rows:
#        print "Next row candidate for a tug is: ", row, " Type code is: ", settings.FLOGGER_FLEET_LIST[row[3]]
        # row[3] is the aircraft registration. Check whether it's a tug or not
#        if settings.FLOGGER_FLEET_LIST[row[3]] > 100 and settings.FLOGGER_FLEET_LIST[row[3]] < 200 :
        if tug_fleet_check(row[3], settings):
            # This is a tug flight
            print "Tug flight found: ", row   
            tug_time = datetime.datetime.strptime("1900/01/01 " + row[1], '%Y/%m/%d %H:%M:%S')  # Tug takeoff time
            flight_count = 0
            for flight in rows: 
#                print "Next row candidate for a glider is: ", flight
                # Check  aircraft type in Flarm_db table is < 3 ie not powered aircraft if no fleet checking
                # or check in fleet_list if fleet checking is being used
                if glider_fleet_check(flight[3], settings):
                    # This is a glider flight
#                    print "Glider flight found: ", flight
                    glider_time = datetime.datetime.strptime("1900/01/01 " + flight[1], '%Y/%m/%d %H:%M:%S')    # Glider takeoff time
                    tdelta_sec = (tug_time - glider_time).total_seconds()      # Difference between 2 times in seconds, note artificially same years, same month, same day
#                    print "Delta tug and glider take-off time is: ", tdelta_sec
                    if int(abs(tdelta_sec)) <= int(settings.FLOGGER_DT_TUG_LAUNCH):                    
                        print "Delta flight time is: ", abs(tdelta_sec), " Glider reg: ", flight[3], " FLOGGER_DT_TUG_LAUNCH is: ", settings.FLOGGER_DT_TUG_LAUNCH
                        # Time difference between takeoff times of glider and tug are less than this (secs), hence assume tug launched glider
                        flight_id = flight[0]
                        flight_details = flight
                        flight_count += 1
                        break
            if flight_count > 1:
                print "Multiple glider flights for a tug flight found - must be false, ignore: ", flight_count
                continue
            if flight_count == 0:
                print "No glider flight found for Tug flight, details: ", row
                continue
            print "Single glider flight found. Glider details: ", flight_details, " Tug details: ", row, " Registration: ", row[3]
            tug_reg = row[3]
            cursor.execute('''SELECT aircraft_model FROM flarm_db WHERE registration=? ''', (tug_reg,))
            tug_model = cursor.fetchone()            
            if tug_model[0] == None:
                print "Aircraft_model not found, try Type for Registration : ", tug_reg
                cursor.execute("SELECT type FROM flarm_db WHERE registration = ?", (tug_reg,))   
                tug_model = cursor.fetchone()
            print "Plane Type/model is: ", tug_model[0]
            try:
                cursor.execute('''UPDATE flights SET tug_registration=?, tug_altitude=?, tug_model=? WHERE id=?''', (row[3], row[4], tug_model[0], flight_id))
                print "Tug model added to flight_id: ", flight_id, " Model: ", tug_model 
                db.commit()
            except:
                print "Failed to add tug model details to flights table for flight: ", flight_details, " tug_model: ", tug_model[0]
        else:
            continue
#            print "Not a tug: ", row
    return
            
        
        
    
    
    
    