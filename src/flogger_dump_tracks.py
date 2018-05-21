
import flogger_settings
import string
import datetime
import time
from time import mktime
import sqlite3
import pytz
from datetime import timedelta
from gpxTracks import gpxTrack
import os



def dump_tracks2(cursor, db, settings):
    print "-------dump_tracks2 Start new dump tracks to gpx file from trackFile table--------"
    if settings.FLOGGER_TRACKS == "Y":
        # This has to change as id in flights is not same as id in flight_log2
        # as the flights table is a processed version of flight_log2, ie deletes short flights (data jitter)
        # and amalgamates others. Correction is to take id in flight_log2 and pass through groups table to flights table
        # For now will dump as gpx some of the tracks but not all (all of the time)
        
        if not os.path.isdir(settings.FLOGGER_TRACKS_FOLDER):  # Create track folder if doesn't exist 
            os.makedirs(settings.FLOGGER_TRACKS_FOLDER)
        
        start_time = datetime.datetime.now()
        gpx_path = str(start_time)
        gpx_path = gpx_path[0:10]
            
        cursor.execute('''SELECT DISTINCT flight_no FROM trackFinal ORDER BY flight_no''')
        flights = cursor.fetchall()
        if flights <> None:
            print "Number of flights in trackFinal is: ", len(flights)
            for aflight in flights:
                flight_no = aflight[0]
                track_file_name = "%s/%s_flight%d_track.gpx" % (settings.FLOGGER_TRACKS_FOLDER, gpx_path, flight_no)
                print "New trackfile name is: ", track_file_name, " This flight is: ", flight_no
                cursor.execute('''SELECT sdate, stime, duration, registration, max_altitude FROM flights WHERE flight_no=?''', (flight_no,))
                flight_data = cursor.fetchone()
                #
                # Insert the track file name into the record for this flight
                #            
                print "Updating flights table, flight_no: ", flight_no, "track_file_name: ", track_file_name
                try:
                    cursor.execute('''UPDATE flights SET track_file_name=? WHERE flight_no=?''', (track_file_name, flight_no)) 
                    db.commit()
                except:
                    print "Failed to add track_file_name to flights table"
                if flight_data <> None:  
                    print "Flight_data is: ", flight_data
                    sdate = flight_data[0]
                    stime = flight_data[1]
                    duration = flight_data[2]
                    registration = flight_data[3]
                    max_altitude = flight_data[4]
                    #
                    # When taking track points from multiple beacons the order received over the Internet might not be the same as the timestamp
                    # of the original data when transmitted by the flarm unit.  Hence it is necessary to order the track points by 
                    # timestamp, assuming the flarm units use GPS time for the timestamp value.
                    #
                    cursor.execute('''SELECT * FROM track WHERE flight_no=? ORDER BY timeStamp''', (flight_no,))
                    tracks = cursor.fetchall()
                    nxt_track = gpxTrack(flight_no, track_file_name, "test", sdate, stime, duration, registration, max_altitude)
                    nxt_track.AddTrackSeg("Track1") 
                    i = 3                               # This was just to check something, easiest to leave it here
                    for track_point in tracks:
                        if i <= 2:
                            print "Trackpoint is: ", track_point
                            i = i + 1
                        else:
                            flight_nos = track_point[1]
                            track_nos = track_point[2]
                            latitude = track_point[3]
                            longitude = track_point[4]
                            altitude = track_point[5]
                            course = track_point[6]
                            speed = track_point[7]
                            timeStamp = track_point[8]
                            #print "timeStamp is: ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timeStamp))
                            nxt_track.AddTrackPnt(longitude, latitude, altitude, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timeStamp)))    # Convert timeStamp float to string
                    nxt_track.EndTrackSeg()
                    nxt_track.EndTrack()
                
                    #
                    # Insert the track file name into the record for this flight
                    #            
                 #   print "Updating flights table, flight_no: ", flight_no, "track_file_name: ", track_file_name
                 #   cursor.execute('''UPDATE flights SET track_file_name=? WHERE flight_no=?''', (track_file_name, flight_no)) 
                 #   db.commit()
                else:
                    print "No flight data in Flights table" 
        else:
            print "No flights in Trackfinal table"  
    else:
        print "Config says: No tracks to dump"
    return