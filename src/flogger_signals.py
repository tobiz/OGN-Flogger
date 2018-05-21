import signal
#import time
#import sqlite3
#from flogger_process_log_old import process_log
#from flogger_process_log import process_log
from flogger_dump_flights import dump_flights
from flogger_dump_tracks import dump_tracks2
from flogger_functions import delete_table

#
#-----------------------------------------------------------------
# Graceful handling of cntrl-c signals
#-----------------------------------------------------------------
#

def sig_handler(db, cursor):
    def inner_sig_handler(signum, frame):
        print 'Cntrl-C pressed'
        #
        # Dump flights table as cvs file
        #
        print "Dump flights table"
        dump_flights()
        #
        # Dump tracks from flights table as .gpx
        #
        print "Dump tracks"
        dump_tracks2(cursor, db)
        #            
        # Delete entries from daily flight logging tables
        #           
        delete_table("flight_log")
        delete_table("flight_log2")
        delete_table("flight_log_final")
        delete_table("flight_group")
        delete_table("flights")
        delete_table("track")
        delete_table("trackFinal")
        delete_table("flarm_db")
        db.commit()
        print "Cntrl-C, exit"
        exit()
    signal.signal(signal.SIGINT, inner_sig_handler)
    return

#signal.signal(signal.SIGINT, sig_handler)

#time.sleep(10) # Press Ctrl+c here