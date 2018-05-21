#
# This function outputs the track data in IGC format.
# For information on IGC format files see: http://carrier.csi.cam.ac.uk/forsterlewis/soaring/igc_file_format/
#
# In general and IGC format file looks Like
# an IGC file that pretty much all display software would be happy with could be:
# AXXX sim_logger v2.31
# HFDTE020911            {HFDTEDDMMYY HFDTE DayMonthYear}
# HFFXA035
# HFPLTPILOTINCHARGE: Ian Forster-Lewis
# HFCM2CREW2: not recorded
# HFGTYGLIDERTYPE:Standard Libelle 201 B
# HFGIDGLIDERID:B21
# HFDTM100GPSDATUM: WGS-1984
# HFRFWFIRMWAREVERSION: 2.31
# HFRHWHARDWAREVERSION: 2009
# HFFTYFRTYPE: sim_logger by Ian Forster-Lewis
# HFGPSGPS:Microsoft Flight Simulator
# HFPRSPRESSALTSENSOR: Microsoft Flight Simulator
# HFCIDCOMPETITIONID:B21
# HFCCLCOMPETITIONCLASS:
# B1140115249652N00212031WA0009600096027000
#
# The track point records have the syntax:
# <record_type><time> <lat> <long>A<alt_P><alt_G> 
#
# Where:
# <record_type = B {basic tracklog record}
# <time> = HHMMSS  {time tracklog entry was recorded}
# <lat> = integerN | integerS {where integer is position data and N|S denotes North or South}
# A = {<alt valid flag> confirming this record has a valid altitude value}
# <alt_P> = integer7 {7 digit integer value of altitude from pressure sensor}
# <alt_G> = integer8 {8 digit integer value of altitude from GPS}
#
# Using commas to denote field separators, you get
# B,110135,5206343N,00006198W,A,00587,00558
#
# Where:
# B: record type is a basic tracklog record
# 110135: <time> tracklog entry was recorded at 11:01:35 i.e. just after 11am
# 5206343N: <lat> i.e. 52 degrees 06.343 minutes North
# 00006198W: <long> i.e. 000 degrees 06.198 minutes West
# A: <alt valid flag> confirming this record has a valid altitude value
# 00587: <altitude from pressure sensor>
# 00558: <altitude from GPS>
#
# Some examples are presented below
# 
# B1101355206343N00006198WA0058700558
# B1101455206259N00006295WA0059300556
# B1101555206300N00006061WA0060300576
#
# This uses aerofiles so do as root eg sudo pip install aerofiles
#
#    REQUIRED_HEADERS = [
#        'manufacturer_code',
#        'logger_id',
#        'date',
#        'logger_type',
#        'gps_receiver',
#    ]
#
# Note.  The 3-letter code used for manufacturer_code is XXX, see IGC spec, section 2.5.6, note 2
#


import flogger_settings
import string
import datetime
import time
from time import mktime
import sqlite3
import pytz
from datetime import timedelta
import os
import aerofiles

def IGC_track_header(file_name, date, registration):
    #
    # Writes the header to an IGC format file using aerofiles
    #
    print "IGC_track_header: ", file_name, " Date: ", date, " Reg: ", registration
    fp = open(file_name, 'w')
    IGC_fp = aerofiles.igc.Writer(fp)
          
    hdate = datetime.date(int(date[0:2])+2000, int(date[3:5]), int(date[6:]))   # Rearrange date from DDMMYY to YYMMDD. The +2000 is a bit
                                                                                # of a cheat but should be ok for a while!
#    hdate = datetime.date(int(date[6:]), int(date[3:5]), int(date[0:2])+2000)  # Rearrange date from DDMMYY to YYMMDD 
    print "IGC_track_header hdate is: ", hdate
    header = {'manufacturer_code': 'XXX',      # XXX is the 3-letter code for unapproved recorder
              'logger_id': 'TBX',
              'date': hdate,
              'fix_accuracy': 50,
              'pilot': 'Not recorded',
              'copilot': 'Not recorded',
              'glider_type': 'Not recorded',
              'glider_id': registration,
              'firmware_version': 'Not recorded',
              'hardware_version': 'Not recorded',
              'logger_type': 'Not recorded',
              'gps_receiver': 'Not recorded',
              'pressure_sensor': 'Not recorded',
              'competition_id': 'Not recorded',
              'competition_class': 'Not recorded',
              }
    try:
        IGC_fp.write_headers(header)
        print "IGC_write_headers OK"
    except ValueError as e:
        print "Write IGC file header failed. ValueError: ", e, " Header= ", header
        return False
    return IGC_fp

def IGC_add_track_point(IGC_fp, longitude, latitude, altitude, time):
    #
    # Output a trackpoint in IGC format
    #
#    print "Write IGC track point"
    hh = int(time[11:13])
    mm = int(time[13:15])
    ss = int(time[15:])
#    print "IGC_add_track_point time is: %s:%s:%s" % (hh, mm, ss)
    try:
#        IGC_fp.write_fix(datetime.time(time[11:13], time[13:15], time[15:]),
        IGC_fp.write_fix(datetime.time(hh, mm, ss),
                         latitude=latitude,
                         longitude=longitude,
                         valid=True,
#                         pressure_alt=altitude,\        # Take default as unknown by OGN Flogger
                         gps_alt=altitude,
#                         extensions=[50, 0, 12],
                         )
    except ValueError as e:
        print "Write IGC track point failed. Reason: ", e
        return False    
    return True


def dump_IGC(cursor, db, settings):
    print "-------Dump tracks to IGC format file from trackFile table--------"
    if settings.FLOGGER_TRACKS_IGC == "Y":
        
        print "Dump tracks in IGC format"
        if not os.path.isdir(settings.FLOGGER_TRACKS_FOLDER):  # Create track folder if doesn't exist 
            os.makedirs(settings.FLOGGER_TRACKS_FOLDER)
        
        start_time = datetime.datetime.now()
        igc_path = str(start_time)[0:10]
            
        cursor.execute('''SELECT DISTINCT flight_no FROM trackFinal ORDER BY flight_no''')
        flights = cursor.fetchall()
        if flights <> None:
            print "Number of flights in trackFinal is: ", len(flights)
            for aflight in flights:
                flight_no = aflight[0]
                track_file_name = "%s/%s_track.new%d.igc" % (settings.FLOGGER_TRACKS_FOLDER, igc_path, flight_no)
                print "New IGC trackfile name is: ", track_file_name, " This flight is: ", flight_no
                cursor.execute('''SELECT sdate, stime, duration, registration, max_altitude FROM flights WHERE flight_no=?''', (flight_no,))
                flight_data = cursor.fetchone()          
                if flight_data <> None:  
                    print "Flight_data is: ", flight_data
                    sdate = flight_data[0]
#                    stime = flight_data[1]
#                    duration = flight_data[2]
                    registration = flight_data[3]
#                    max_altitude = flight_data[4]
                    #
                    # When taking track points from multiple beacons the order received over the Internet might not be the same as the timestamp
                    # of the original data when transmitted by the flarm unit.  Hence it is necessary to order the track points by 
                    # timestamp, assuming the flarm units use GPS time for the timestamp value.
                    #
                    cursor.execute('''SELECT * FROM track WHERE flight_no=? ORDER BY timeStamp''', (flight_no,))
                    tracks = cursor.fetchall()
                    IGC_fp = IGC_track_header(track_file_name, sdate, registration)
                    i = 3                               # This was just to check something, easiest to leave it here
                    for track_point in tracks:
                        if i <= 2:
                            print "IGC Trackpoint is: ", track_point
                            i = i + 1
                        else:
#                            flight_nos = track_point[1]
#                            track_nos = track_point[2]
                            latitude = track_point[3]
                            longitude = track_point[4]
                            altitude = track_point[5]
#                            course = track_point[6]
#                            speed = track_point[7]
                            timeStamp = track_point[8]
                            #print "timeStamp is: ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timeStamp))
                            if IGC_add_track_point(IGC_fp, longitude, latitude, altitude, time.strftime("%Y-%m-%d %H%M%S", time.localtime(timeStamp))) == False :  # Convert timeStamp float to string
                                print "IGC_add_track_point failed"
                                return
                
                else:
                    print "No flight data in Flights table"
#            fp.close() 
        else:
            print "No flights in Trackfinal table"  
    else:
        print "Config says: Don't dump tracks in IGC format"
    return

