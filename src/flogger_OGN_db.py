#    
#-----------------------------------------------------------------
# Function to read OGN Flarm database and create SQLite version for local use.
# Note this means if a new entry is added to OGN db after flogger has started
# it won't be included.  
#
# Run at start of each day? 
#
# Access to OGN Flarm db: http://ddb.glidernet.org/download/?t=1
#-----------------------------------------------------------------
#
import string
import requests
import sqlite3
import time
import flogger_settings
#import flogger_OGN_db 
# import unicodedata



def ogndb (ognurl, cursor, flarmdb, flarm_data, settings):
    #    
    #-----------------------------------------------------------------
    # This function reads the file of Flarm units registered on OGN and
    # uses this to build the flarm_db. 
    # It takes data from units which are registered for aircraft that are to be logged   
    #
    # Various options exist for accessing the OGN db in different formats
    # Simple basic data:
    #     "http://ddb.glidernet.org/download"
    # Basic data plus field for "Aircraft Type"
    #     "http://ddb.glidernet.org/download/?t=1!
    # In a flarmnet-compatible format
    #     "http://ddb.glidernet.org/download/download-fln.php"   
    #
    # Format is:
    #     DEVICE_TYPE(0),DEVICE_ID(1),AIRCRAFT_MODEL(2),REGISTRATION(3),CN(4),TRACKED(5),IDENTIFIED(6),AIRCRAFT_TYPE(7)
    #
    # Aircraft Type values (hard coded for now):
    #    1 => 'Gliders/motoGliders',
    #    2 => 'Planes',
    #    3 => 'Ultralights',
    #    4 => 'Helicopters',
    #    5 => 'Drones/UAV',
    #    6 => 'Others',
    #-----------------------------------------------------------------
    #  
    try:
        print "flogger_OGN_db.py: Create flarm_db table"
        cursor.execute('''CREATE TABLE IF NOT EXISTS
                            flarm_db(id INTEGER PRIMARY KEY, type TEXT, flarm_id TEXT, airport STRING, aircraft_model TEXT, registration TEXT, radio TEXT, aircraft_type TEXT)''')
        print "flarm_db table created"
    except Exception as e:
        # Roll back any change if something goes wrong
        print "Failed to create flarm_db"
#        dbflarm.rollback()
#        raise e 
    try:
        print "OGN flarm db is at http://ddb.glidernet.org/download"
        ogn_db = settings.FLOGGER_OGN_DB_URL
        print "settings.FLOGGER_OGN_DB_URL is: ", settings.FLOGGER_OGN_DB_URL
        r = requests.get(ogn_db)
        print "requests.get(ogn_db) with: ", settings.FLOGGER_OGN_DB_URL
    except Exception as e:
        print "Failed to connect to OGN db, reason: %s. Exit" % (e)
#        exit()
    print "OGN db accessed"   
    
    data = r.content  
#    print "OGN content is: ", data[0], data[1], data[2]
    lines = data.split("\n")
#    print "OGN split is: ", lines
    i = 1
    for line in lines:
        if i == 1:
            i += 1
            continue        # Discard first line
#        print "Line ", i, " is: ", line
        if line == "":
            # Seems to be a blank line at end
            continue        # Discard last line
        line = line.replace("'", "")            # Remove all "'" characters
        line = line.replace("\r", "")           # Remove "\r" at end of line in last field
        fields = line.split(",")                # Split line into fields on comma boundaries then remove any quote marks
#        print "Fields: ", fields
        #     DEVICE_TYPE(0),DEVICE_ID(1),AIRCRAFT_MODEL(2),REGISTRATION(3),CN(4),TRACKED(5),IDENTIFIED(6),AIRCRAFT_TYPE(7)
        nf0 = fields[0]        # Device Type:  - ICAO (I)  - ICAO type address (in practice FLARM device with assigned ICAO address)
                               #               - FLARM (F) - obvious  (flarm "hardware" id)
                               #               - OGN (O)   - used for OGN trackers 
        nf1 = fields[1]        # Flarm ID
        nf2 = fields[2]        # Aircraft Model
        nf3 = fields[3]        # Aircraft Registration
        nf4 = fields[4]        # CN
        nf5 = fields[5]        # Tracked
        nf6 = fields[5]        # Identified
        nf7 = fields[7]        # Aircraft Type
#        print "Line: ", i, " Fields: ", nf1, " ", nf0, " ", nf3
        if settings.FLOGGER_FLEET_LIST.has_key(nf3):
            airport = settings.FLOGGER_AIRFIELD_NAME
        else:
            airport = "OTHER" 
#        if int(nf7) > 2:
#        if int(nf7) > 3:
            # Type 2 is 'Plane', Type 3 is 'Ultralight'
#            print "Ignore Aircraft type is: ", nf7
#            continue
#        elif "n" in settings.FLOGGER_LOG_TUGS or "N" in settings.FLOGGER_LOG_TUGS and int(nf7) == 2: 
#                print "Ignore tugs: ", nf7
#                continue
            
        Registration = nf3
        aircraft_type = 0
        try:
            aircraft_type_val = settings.FLOGGER_FLEET_LIST[Registration]
            if aircraft_type_val >= 1 and aircraft_type_val < 100:
                aircraft_type = 1
            if aircraft_type_val >= 100 and aircraft_type_val < 200:
                aircraft_type = 2
            if aircraft_type_val >= 200 and aircraft_type_val < 300:
                aircraft_type = 1  
#            print "Fleet list aircraft: ", Registration, " Type: ", str(aircraft_type)             
        except:
#            pass
            aircraft_type = nf7
#            print "Aircraft not in fleet list: ", Registration, " Type: ", str(aircraft_type)
#            if type(Registration) == 'ascii':
#                pass  
#            else:
#                print "Non ascii in: ", Registration
#                Registration = Registration.encode('ascii','ignore')
#                print "After encode: ", Registration
        aircraft_type = str(aircraft_type) 
         
        try:
            cursor.execute('''INSERT INTO flarm_db(type, flarm_id, airport, aircraft_model, registration, aircraft_type)
                               VALUES(:type, :flarm_id, :airport, :aircraft_model, :registration, :aircraft_type)''',
#                                {'type': nf0, 'flarm_id': nf1, 'airport': settings.FLOGGER_AIRFIELD_NAME, 'type': nf0, 'registration': nf3})
#                                {'type': nf0, 'flarm_id': nf1, 'airport': airport, 'aircraft_model':  nf2, 'registration': nf3, 'aircraft_type': nf7})
                                {'type': nf0, 'flarm_id': nf1, 'airport': airport, 'aircraft_model':  nf2, 'registration': nf3, 'aircraft_type': aircraft_type})
        except Exception as e:
           print "Flarm_db insert failed. Reason: %s Aircraft: %s Flarm_ID: %s" % (e, Registration, nf1)
        i += 1
    flarmdb.commit()
    return True
#    exit()

#    print "First line from OGN data is : ", val
    
 
#db = sqlite3.connect(settings.FLOGGER_DB_NAME)
#cursor = db.cursor()                            # Get a cursor object
#f = open(settings.FLOGGER_DB_SCHEMA, 'rt')      # Open the db schema file for reading
#schema = f.read()
#cursor.executescript(schema)                    # Build flogger db from schema
#print "End of building db: ", settings.FLOGGER_DB_NAME, " using schema: ", settings.FLOGGER_DB_SCHEMA



#    
#-----------------------------------------------------------------
# Build local database from OGN of aircraft    
#-----------------------------------------------------------------
#
   
#print "Start build OGN DB: Test"
#t1 = time.time() 
#if ogndb("http://ddb.glidernet.org/download", cursor, db, "flarm_data") == True:
#    print "OGN db built"
#else:
#    print "OGN db build failed, exit"
#t2 = time.time()
#print "End build OGN DB in ", t2 - t1 , " seconds"

