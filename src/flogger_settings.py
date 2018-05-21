
class class_settings():
    #-------------------------------------
    # OGN-Flight-Logger Settings
    #
    # This class is used to created the user defined values used by flogger
    # This is NOT where the settings are held over each invocation of flogger, these
    # are held in: flogger_setting_file.txt (probably to be renamed ".config", but not yet!) 
    #-------------------------------------
    # Python APRS/OGN program to log flight times, durations, maximum heights achieved and tracks
    #
    # This python program creates an SQlite db of flights from a given location and aircraft list 
    # (the later two parameters are to be be developed into a more generalised format).#
    #
    # At the moment this is very much 'in development'#
    #
    # To install OGN Flight Logger the following prerequisites are required
    # - python-tz
    # - sqlite3
    # - libfap
    #
    # If installing on an arm based system this can be achieved by:
    #
    # sudo apt-get install python-tz sqlite3
    # wget http://www.pakettiradio.net/downloads/libfap/1.5/libfap6_1.5_armhf.deb
    # sudo dpkg -i libfap*.deb
    
    #
    #-------------------------------------
    # Setting values
    #
    # The values APRS_SERVER_HOST and APRS_SERVER_PORT are FIXED
    # All other values should be set for a specific location and USER/PASSCODE
    # Failure to change USER/PASSCODE results in an error
    #-------------------------------------
    #
    
    # APRS_SERVER_HOST = 'rotate.aprs2.net'
    # APRS_SERVER_PORT = 14580
    APRS_SERVER_HOST = "aprs.glidernet.org"
    APRS_SERVER_PORT = 14580
    #
    # Please get your own Username and Passcode from http://www.george-smart.co.uk/wiki/APRS_Callpass
    # DO NOT USE THE VALUES IN THIS FILE AS IT WILL STOP A PREVIOUS INVOCATION WORKING CORRECTLY
    #
#    APRS_USER = "PythonEx"# Username
    APRS_USER = ""# Username
    APRS_PASSCODE = 1234# Passcode. See http://www.george-smart.co.uk/wiki/APRS_Callpass 
    #
    # Check that APRS_USER and APRS_PASSCODE are set
    #
    #assert len(APRS_USER) > 3 and len(str(APRS_PASSCODE)) > 0, 'Please set APRS_USER and APRS_PASSCODE in settings.py.'
    #
    # User defined configuration values
    #
    
    #
    # This value for base Directory for relative files, ie: 
    # - flogger_schema-1.0.4.sql
    # - logs
    # - tracks
    ##import sys, os
    ##file = sys.argv[0]
    pathname = "os.path.dirname(file)"
    #FLOGGER_BS = "/home/pjr/git_neon/OGN-Flight-Logger_V2/"
    FLOGGER_BS = ''
    #FLOGGER_BS = "/home/pi/workspace/OGN-Flight-Logger_V2.1/"       
    
    FLOGGER_MODE = "test"   # Test or live mode
#    FLOGGER_DB_SCHEMA = 'FLOGGER_BS + "flogger_schema-1.0.4.sql"'# File holding SQLite3 database schema  
#    FLOGGER_DB_SCHEMA =  "flogger_schema-1.0.4.sql"     # File holding SQLite3 database schema    
    FLOGGER_DB_SCHEMA =  ""     # File holding SQLite3 database schema    
    #FLOGGER_QNH = 340                                               # QNH ie ASL in metres for airfield at lat/logitude, if set to 0, elevation is automatically looked up. This is Sutton Bank    
    FLOGGER_QNH = 0# QNH ie ASL in metres for airfield at lat/logitude, if set to 0, elevation is automatically looked up. This is Sutton Bank
    FLOGGER_LATITUDE = +54.228833                           # Latitude, longitude of named OGN receiver airfield 
    FLOGGER_LONGITUDE =  -1.209639                       # Latitude, longitude of named OGN receiver airfield 
    #FLOGGER_AIRFIELD_DETAILS = ""                                  # Location details for use by geocoder. If blank, "" use LAT, LONG etc
    FLOGGER_AIRFIELD_DETAILS = "Yorkshire Gliding Club UK"  # Location details for use by geocoder. If blank, "" use LAT, LONG etc
    FLOGGER_MIN_FLIGHT_TIME = "0:4:0" # Minimum time for duration to be considered a flight, hh:mm:ss
    FLOGGER_KEEPALIVE_TIME = 900# Interval in seconds for sending tcp/ip keep alive on socket connection
    FLOGGER_DB_NAME = "flogger.sql3.2"# Name of file for flogger SQLite3 database
    FLOGGER_FLARMNET_DB_URL = "http://www.flarmnet.org/files/data.fln"# URL of Flarmnet database
    #FLOGGER_OGN_DB_URL = "http://ddb.glidernet.org/download"        # URL of OGN Flarm database  or blank for don't use   
    FLOGGER_OGN_DB_URL = "http://ddb.glidernet.org/download/?t=1"# URL of OGN Flarm database  or blank for don't use   
#    FLOGGER_OGN_DB_URL = "http://ddb.glidernet.org/download/?t=1"# URL of OGN Flarm database  or blank for don't use                        
    #FLOGGER_OGN_DB_URL = ""                                        # URL of OGN Flarm to registration mapping database  
    #FLOGGER_AIRFIELD_NAME = "SuttonBnk"                            # Name of Flarm base station for airfield. NOTE MUST BE PROVIDED
    FLOGGER_AIRFIELD_NAME = "SUTTON BANK"# Name of Flarm base station for airfield. NOTE MUST BE PROVIDED AS in flarmdb record
    # If blank, "" then all aircraft in db are included in logs & tracks
    
    #FLOGGER_FLEET_CHECK = "Y"                                       # Checks Flarm ID is for aircraft fleet of FLOGGER_AIRFIELD_NAME if "Y"
    FLOGGER_FLEET_CHECK = "N"            # Checks Flarm ID is for aircraft fleet of FLOGGER_AIRFIELD_NAME if "Y"
    FLOGGER_QFE_MIN = 100# Minimum altitude in metres attained for inclusion as a flight, ie ~300 ft
#    FLOGGER_LOG_PATH = 'FLOGGER_BS + "logs"'# Path where log files are stored 
    FLOGGER_LOG_PATH = "logs"# Path where log files are stored 
    FLOGGER_TRACKS = "Y"    # If Y flight tracks are recorded. Default is N, ie No tracks logged
    FLOGGER_TRACKS_FOLDER = ''# Folder for .gpx files for flight tracks
    FLOGGER_V_SMALL = 10.0# Lowest moving speed to be considered as zero kph
    FLOGGER_NAME = "OGN_Flogger"# Name to be displayed on APRS
    FLOGGER_VER = "0.3.1"    # Flogger version number
#    FLOGGER_RAD = 50# APRS radius in km from base station in AIRFIELD_DETAILS
    FLOGGER_RAD = 0# APRS radius in km from base station in AIRFIELD_DETAILS
#    FLOGGER_FLIGHTS_LOG = ''# Folder for csv file of daily flights record  
    FLOGGER_FLIGHTS_LOG = "flight_logs"# Folder for csv file of daily flights record  
    FLOGGER_DATA_RETENTION = 3# Number of days to keep .csv files, ie delete, if "0" keep all files
    FLOGGER_LOG_TUGS = "Y"  # Don't log tug flights if "N"
    FLOGGER_TRACKS_IGC = "N"    # Dump flight tracks in IGC format if "Y" else no
    FLOGGER_LOG_TIME_DELTA = -1# Number of hours before sunset to start processing flight log
    FLOGGER_SMTP_SERVER_URL = ""# URL of smtp server for sending email
    FLOGGER_SMTP_SERVER_PORT = 0# smtp server port number, normally 25
    FLOGGER_SMTP_TX = ""    # Flight log sender email addrs
    FLOGGER_SMTP_RX = ""    # Flight log receiver email addrs 
    FLOGGER_AIRFIELD_LIMIT = 2000   # Distance from airfield centre considered a 'Land Out' in metres
    FLOGGER_LANDOUT_MODE = "email"                                  # Send land out msg by "email', SMS, or "" don't send
    FLOGGER_TAKEOFF_EMAIL = "Y" # Send email for each take off if Yes else no
    FLOGGER_LANDING_EMAIL = "Y"   # Send email for each landing if Yes else no
    FLOGGER_LOG_LAUNCH_FAILURES = "N" # Log launch failures, ie below min time & min height
    FLOGGER_LOCATION_HORIZON = "-0:34"  # Adjustments for angle to horizon for sunset
    FLOGGER_V_TAKEOFF_MIN = 10# Min ground speed considered as takenoff. ogn-live is (55Km/h)
    FLOGGER_V_LANDING_MIN = 10# Min ground speed considered as landed. ogn-live is (40Km/h)
    FLOGGER_DT_TUG_LAUNCH = 20# Delta t(sec) between glider and tug takeoff times to be tug launched
    FLOGGER_DUPLICATE_FLIGHT_DELTA_T = "0:1:00"    # Delta between two landing & takeoff times of same aircraft to be different flights
    FLOGGER_DUPLICATE_FLIGHT_DELTA = 90# Delta time (secs) for duplicate flights
    #
    # The following fields are used to determine if data from APRS is a position packet from any 1 of up to 4 OGN receivers base stations.
    # The OGN receiver areas can overlap and if more then 1 is supplied it will increase the accuracy of both the data and track results
    # The list of OGN receivers can be found at http://wiki.glidernet.org/list-of-receivers. The field values are strings for any
    # APRS AIRFIELDS code value.  One or more must be specified.
    # If a value is not needed use a null string, ie "". Coordinates for the primary OGN receiver station are either supplied
    # by FLOGGER_LATITUDE, FLOGGER_LONGITUDE values or if these are not supplied then those returned by a geolocator
    # service using FLOGGER_AIRFIELD_DETAILS. The primary OGN receiver base station coordinates together with the value 
    # of FLOGGER_RAD are used to filter the data received from APRS.
    #                   
    
    #FLOGGER_APRS_BASE_1 = "SuttonBnk"                  
    #FLOGGER_APRS_BASE_2 = "UKPOC"           
    #FLOGGER_APRS_BASE_3 = "UKRUF"         
    #FLOGGER_APRS_BASE_4 = "Linton"
    
    FLOGGER_APRS_BASES = ["SuttonBnk", "UKPOC", "UKRUF", "Linton", "Riponhill"]  
    
    
    # Coded       001-099: Gliders, 
    #             101-199: Tugs, 
    #             201-299: Motor Gliders, 
    #             301-399: Other
    # Note. No reason for coding these values other than, 'why not!'
    FLOGGER_FLEET_LIST = {"G-CHEF":1, "G-CHVR":2, "G-CKFN":3, "G-CKJH":4, 
                          "G-CKLW":5, "G-CJVZ":6, "G-DDKC":7, "G-DDPO":8,  
                          "G-BETM":101, "G-CIOF":102, "G-MOYR":103, "G-BJIV": 104,
                          "G-OSUT":201, 
                          }
    #
    # Aircraft types in OGN Database, see https://github.com/glidernet/ogn-ddb/blob/master/index.php#L87
    #
    ##FLOGGER_AIRCRAFT_CAT = [
    ##        'None'                  # 0 = Blank
    ##        'Gliders/motoGliders',  # 1
    ##        'Planes',               # 2
    ##        'Ultralights',          # 3
    ##        'Helicopters',          # 4
    ##        'Drones/UAV',           # 5
    ##        'Others',               # 6
    ##        ]
    
    
# Flogger process control. Continue process loop if True, else terminate thread
    FLOGGER_RUN = True
    FLOGGER_INCLUDE_TUG_FLIGHTS = "N"    # If Yes display tug flights as separate lines in gui flight log





 
