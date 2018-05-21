#    
#-----------------------------------------------------------------
# Function to read flarm_id database and create SQLite version for local use.
# Note this means if a new entry is added to Flarmnet after flogger has started
# it won't be included. Maybe this should be run at the start of each day?  
# Flarmnet holds its data as the hex coding of the characters.
# The function reads this format into its own local file converting it to
# character form (ie 2 pairs of hex digits become 1 character) 
# before creating the database of records.
#
# Note:
# Flarmnet database URL is:    http://www.flarmnet.org/files/data.fln
# OGN database URL is:         http://ddb.glidernet.org/download/?t=1
#-----------------------------------------------------------------
#
import string
import requests
import sqlite3
import time
import flogger_settings
from flogger_OGN_db import ogndb
# import unicodedata

# def flarmdb (flarmnet, flogger_db, flarm_data):
def flarmdb (flarmnet, cursor, database, flarm_data, settings):
    #    
    #-----------------------------------------------------------------
    # Initialise flarm table in local db with Flarm ID to registration mappings.
    # This can be from Flarmnet or OGN, use OGN by default    
    #-----------------------------------------------------------------
    #
    #
    print "flarmdb use: ", settings.FLOGGER_OGN_DB_URL
    if settings.FLOGGER_OGN_DB_URL <> "":
        print "Use OGN database"
        ogndb(settings.FLOGGER_OGN_DB_URL, cursor, database, flarm_data, settings)
        return True
    print "Use Flarmnet database"   
    dbflarm = database
    try:
        # flarmnet_db is at "http://www.flarmnet.org/files/data.fln"
        flarmnet_db = flarmnet
        r = requests.get(flarmnet_db)
    except:
        print "Failed to connect to flarmnet db, exit"
        exit()
        
    print "flarm_data is: ", flarm_data    
    data = r.content    
#    flm = open("flarm_data", "w")
#    flm_txt = open("flarm_data_txt", "w")  
    flm = open(flarm_data, "w")
    flm_ln = len(r.content) - 1
    print "Flarm db length: ", flm_ln
    try:
        for i in range(0, flm_ln, 1):
            c = "%c" % data[i]
            flm.write(c)
    except :
        print "Error writing flarm_data"   
        exit()
    flm.close()
    
    # db = open("data.fln", 'r')
    db = open(flarm_data, 'r')
    # Read first line and convert to number
    x = db.readline()
    val = int(x, 16)
    print "First line from FlarmNet data is : ", val
    
    try:
        print "flarm_db.py: Create flarm_db table"
        cursor.execute('''CREATE TABLE IF NOT EXISTS
                            flarm_db(id INTEGER PRIMARY KEY, flarm_id TEXT, airport STRING, type TEXT, registration TEXT, radio TEXT)''')
        print "flarm_db table created"
    except Exception as e:
        # Roll back any change if something goes wrong
        print "Failed to create flarm_db"
        dbflarm.rollback()
        raise e
    
    i = 1
    line = ""
    nos_lines = val 
    while True:
        try:
            line = db.readline()
            line_lng = len(line)
#            print "Line length is: ", line_lng
            string = ""
#            print "read: ", i, " returns: ", line
            for j in range(0, 172, 2):
                c = chr(int(line[j:j + 2], 16))
                string = string + c
            i = i + 1
#            print "FlarmBD line: ", string
    #        v.decode("iso-8859-15").encode("utf-8")
            ID = str(string[0:6]).decode("iso-8859-15").encode("utf-8")
    #        Airport = str(string[27:47]).decode("iso-8859-15").encode("utf-8", errors="replace")
            try:
                Airport = str(string[27:47]).decode("utf-8").encode("iso-8859-15")
#                Airport = str(string[27:47]).decode("iso-8858-15").encode("iso-8859-15")
                Airport = Airport.rstrip()
            except:
                print "Code error ", str(string[27:47]), " Row: ", i
            Type = str(string[48:69]).decode("iso-8859-15").encode("utf-8")
            Registration = str(string[69:75]).decode("iso-8859-15").encode("utf-8")
            Radio = str(string[79:86]).decode("iso-8859-15").encode("utf-8")
    #        print "Line: ", i-1, " ID: ", ID,  " Airport: ", Airport, " Type: ", Type, " Registration: ", Registration,  " Radio: ", Radio
    #        row = "%s__%s__%s__%s__%s\n" % (ID, Airport, Type, Registration, Radio)
    #        flm_txt.write(row)

    #
    #        Start Add aircraft type for tug logging
    #
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
                aircraft_type = 1    # Since it's not in the fleet list can't be a tug hence assume it's a glider
    #            print "Aircraft not in fleet list: ", Registration, " Type: ", str(aircraft_type)
            aircraft_type = str(aircraft_type)              
    #
    #        End Add aircraft type for tug logging
    #

            # Note 'type': "F" is used as it means: Flarm device. Since this is taken from the Flarmnet db seems reasonable default
            # since no value is supplied, to be compatible with OGN db
            try:
                    cursor.execute('''INSERT INTO flarm_db(type, flarm_id, airport, aircraft_model, registration, aircraft_type)
                                       VALUES(:type, :flarm_id, :airport, :aircraft_model, :registration, :aircraft_type)''',
                                        {'type': "F", 'flarm_id': ID, 'airport': Airport, 'aircraft_model':  Type, 'registration': Registration, 'aircraft_type': aircraft_type})
#            try:
#                cursor.execute('''INSERT INTO flarm_db(flarm_id, airport, type, registration, radio, aircraft_type)
#                               VALUES(:flarm_id, :airport, :type, :registration, :radio, :aircraft_type)''',
#                                {'flarm_id': ID, 'airport': Airport, 'type': Type, 'registration': Registration, 'radio': Radio, 'aircraft_type': aircraft_type})
    #            dbflarm.commit()
            except :
               print "Flarm_db insert failed ", Airport
               dbflarm.commit()
               return False
        except:
            print "Number of rows is: ", i - 1
#            dbflarm.commit()
            dbflarm.commit()
            return True
    return True
    # dbflarm.commit()

   
# print "Start build Flarm DB: Test"
# t1 = time.time() 
# flarmdb("http://www.flarmnet.org/files/data.fln", 'flogger.sql3', "flarm_data")
# t2 = time.time()
# print "End build Flarm DB in ", t2 - t1 , " seconds"

