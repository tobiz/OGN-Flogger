
# 20150921            Problem! If the pair after a "Same flight" pair is found to be a "Different flight" then it will be 
#                     given the group_id  of the last "Same flight, ie wrong!  Next needs to given the next value of group_id 
# 20150922            Modified the total flight time code for a flight group
#
# 20160424            Rewrite of phase 2 processing to correct errors. Code could be 'gardened' to make neater and simpler
# 

import flogger_settings
#import settings
import string
import datetime
import time
from time import mktime
import sqlite3
import pytz
from datetime import timedelta
import gpxTracks

def addFinalTrack(cursor, flight_no, track_no, longitude, latitude, altitude, course, speed, timeStamp, settings):
    #    
    #-----------------------------------------------------------------
    # Add gps track data to trackFinal record if settings.FLOGGER_TRACK is "Y" ie yes    
    #-----------------------------------------------------------------
    #

    if settings.FLOGGER_TRACKS == "Y":
#        print "Adding trackFinal data to: %i, %i, %f, %f, %f, %f %f " % (flight_no, track_no, latitude, longitude, altitude, course, speed)
        cursor.execute('''INSERT INTO trackFinal(flight_no,track_no,latitude,longitude,altitude,course,speed,timeStamp) 
            VALUES(:flight_no,:track_no,:latitude,:longitude,:altitude,:course,:speed,:timeStamp)''',
            {'flight_no':flight_no, 'track_no':track_no, 'latitude':latitude, 'longitude':longitude, 'altitude':altitude, 'course':course, 'speed':speed, 'timeStamp':timeStamp})
    return

def txt2time(txt_time):
    #    
    #-----------------------------------------------------------------
    # Retuns a time in txt string of HH:MM:SS in a format for simple arithmetic
    #-----------------------------------------------------------------
    #
    print "txt2time param is: ", txt_time
    res = datetime.datetime.strptime("1900/01/01 " + str(txt_time), '%Y/%m/%d %H:%M:%S')
    print "txt2time result is: ", res
    return res
    

#
#-----------------------------------------------------------------
# Process the log of each record in 'flight_log' into table 'flights' to create
# table flight_log2 where each flight is take off to landing, any ground movements etc.,
# having been removed. Process_log assumes the database tables have been created in the 
# calling environment such that only the cursor to the database needs be passed
#-----------------------------------------------------------------
#
def process_log (cursor, db, settings):
    MINTIME = time.strptime(settings.FLOGGER_MIN_FLIGHT_TIME, "%H:%M:%S")  # 5 minutes minimum flight time
    print "MINTIME is: ", MINTIME
    cursor.execute('''SELECT max(sdate) FROM flight_log''')
    row = cursor.fetchone()
    print "row is: ", row
    #    
    #-----------------------------------------------------------------
    # Phase 0 processing start  
    #-----------------------------------------------------------------
    #
    # Check flight_log for duplicates and report
    # There shouldn't be any! For now just report
    #
    print "+++++++Phase 0 Start+++++++"
    cursor.execute('''SELECT DISTINCT sdate, stime, edate, etime, duration, src_callsign, registration FROM flight_log_final''')
    distincts = cursor.fetchall()
    cursor.execute('''SELECT sdate, stime, edate, etime, duration, src_callsign, registration FROM flight_log_final''')
    all = cursor.fetchall()
    if len(all) > len(distincts):
        print "*** Duplicates found in flight_log_final. Nos is: ", len(all) - len(distincts)
    else:
        print "*** No duplicates found ***"
    #    
    #-----------------------------------------------------------------
    # Phase 0 processing end 
    #-----------------------------------------------------------------
    #
    
    
    #    
    #-----------------------------------------------------------------
    # Phase 1 processing    
    #-----------------------------------------------------------------
    #
    # This phase examines flight_log_final and from this removes flights which are too short
    # and or which don't attain a sufficient altitude. These are written to flight_log.
    #
    # The following takes into account the situation when there are no records in flight_log
    # and there is therefore no highest date record. Note it does require that this code is
    # run on the same day as the flights are recorded in flight_log_final
    #
    # Note this may need revision for the case that the system is started before sunrise. Not sure
    #
    print "+++++++Phase 1 Start+++++++"  
    print "settings.FLOGGER_QNH: ", settings.FLOGGER_QNH 
    if row <> (None,):
        max_date = datetime.datetime.strptime(row[0], "%y/%m/%d")
        print "Last record date in flight_log is: ", max_date
    else:
        print "No records in flight_log so set date to today"
        today = datetime.date.today().strftime("%y/%m/%d")
        max_date = datetime.datetime.strptime(today, "%y/%m/%d")
        
    print "max_date set to today: ", max_date
      
    
    cursor.execute('''SELECT sdate, stime, edate, etime, duration, src_callsign, max_altitude, speed, registration, flight_no FROM flight_log_final''')
    data = cursor.fetchall()
    for row in data:
        print "Flight_log_final row is: sdate %s, stime %s, edate %s, etime %s, duration %s, src_callsign %s, altitude %s, speed %s, registration %s, flight_no: %d" % (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
    #    print "Row is: sdate %s" % row[0] 
    #    print "stime %s " % row[1] 
    #    print "edate %s " % row[2]
    #    print "etime %s " % row[3]
    #    print "duration %s " % row[4]
    #    print "src_callsign %s " % row[5]
    #    print "altitude %s " % row[6]
    #    print "speed %s"  % row[7]
    #    print "registration %s" % row[8]
    #    print "flight_no is: %d % row[9]
    
        time_str = row[4].replace("h", "")
        time_str = time_str.replace("m", "")
        time_str = time_str.replace("s", "")
        print "Duration now: ", time_str
        duration = time.strptime(time_str, "%H: %M: %S")
        
        strt_date = datetime.datetime.strptime(row[0], "%y/%m/%d")
        if strt_date >= max_date:
            print "**** Record start date: ", strt_date, " after last flight_log record, copy: ", max_date
            print "Flight duration is: ", duration, " MINTIME is: ", MINTIME
            delta_alt = (float(row[6]) - (float(settings.FLOGGER_QNH) + float(settings.FLOGGER_QFE_MIN)))
            print "Delta altitude is: ", delta_alt
            if duration > MINTIME:
                print "#### Copy record. Duration is: ", time_str
                cursor.execute('''INSERT INTO flight_log(sdate, stime, edate, etime, duration, src_callsign, max_altitude, speed, registration, flight_no)
                                    VALUES(:sdate,:stime,:edate,:etime,:duration,:src_callsign,:max_altitude,:speed, :registration, :flight_no)''',
                                    {'sdate':row[0], 'stime':row[1], 'edate': row[2], 'etime':row[3],
                                    'duration': row[4], 'src_callsign':row[5], 'max_altitude':row[6], 'speed':row[7], 'registration':row[8], 'flight_no': row[9]})
                print "Row copied"
#            else:
            elif (float(row[6]) - (float(settings.FLOGGER_QNH) + float(settings.FLOGGER_QFE_MIN))) <= 0:
#                print "xxxx Flight duration less than or equal to MINTIME: ", duration, " Check altitude xxxx"
                # Note this needs a major enhancement to store the altitude at take off
                # For now make it simple. Needs better solution, eg add takeoff alt to db
#                if row[6] <= (settings.FLOGGER_QNH + settings.FLOGGER_QFE_MIN):
                print "====Ignore row, flight time too short and too low. Time: ", row[4], " alt: ", row[6], " QNH Min: ", (settings.FLOGGER_QNH + settings.FLOGGER_QFE_MIN)
#                else:
            elif (float(row[6]) - (float(settings.FLOGGER_QNH) + float(settings.FLOGGER_QFE_MIN))) > 0:
                print "++++Accept row, short flight but ok min height. Time: ", row[4], " alt: ", row[6], " QNH Min: ", (settings.FLOGGER_QNH + settings.FLOGGER_QFE_MIN)
                cursor.execute('''INSERT INTO flight_log(sdate, stime, edate, etime, duration, src_callsign, max_altitude, speed, registration,flight_no)
                                VALUES(:sdate,:stime,:edate,:etime,:duration,:src_callsign,:max_altitude,:speed, :registration,:flight_no)''',
                                {'sdate':row[0], 'stime':row[1], 'edate': row[2], 'etime':row[3],
                                'duration': row[4], 'src_callsign':row[5], 'max_altitude':row[6], 'speed':row[7], 'registration':row[8], 'flight_no':row[9]})
        else:
            print "???? Record start date: ", strt_date, " before last flight_log record, ignore: ", max_date
    print "-------Phase 1 End--------"
    db.commit()  

#def process_groups():
    #    
    #-----------------------------------------------------------------
    # Phase 2 processing    
    #-----------------------------------------------------------------
    #
    # Phase 2 processing
    # This phase examines all the records and puts them into groups such that each group has 
    # an end and start time, such that a group is a distinct flight ie their end and start times are greater than
    # TIME_DELTA, and not just therefore data jiggles (eg moving the plane to a new position on the flight line),
    # ie the end and start time of subsequent flights is such that it couldn't have been a real flight
    # For some records for each flight the end time and next start time are too close together
    # to be independent flights.
    # This phase examines flight_log and forms them into flights made by each aircraft as denoted 
    # by registration, the result being held in flight_group.
    #
    
    print "+++++++Phase 2: Process Groups. Start+++++++"
    time_lmt = datetime.datetime.strptime(str(settings.FLOGGER_DUPLICATE_FLIGHT_DELTA_T), "%H:%M:%S") - datetime.datetime.strptime("0:0:0", "%H:%M:%S")
    lmt_secs = time_lmt.total_seconds()         # lmt_secs is a constant so compute once
    group = 0                                   # Number of groups set for case there are none
    
    cursor.execute('''SELECT DISTINCT src_callsign FROM flight_log ORDER BY sdate, stime ''')
    all_callsigns = cursor.fetchall()
    print "All call_signs: ", all_callsigns
    for acallsign in all_callsigns:
        call_sign = acallsign[0]                # acallsign is a tuple
        prev_stime = "0:0:0"                    # Initialise previous stime for comparison purposes for this group
        print "Processing for call_sign: ", call_sign
          
        cursor.execute('''SELECT sdate, stime, edate, etime, duration, src_callsign, max_altitude, registration , flight_no
                         FROM flight_log WHERE src_callsign=?
                         ORDER BY sdate, stime ''', (call_sign,))
        
        rows = cursor.fetchall()                # rows is all flight records for an aircraft with callsign
        row_count = len(rows)
        print "Number of rows is: ", row_count
        for r in rows:  # This will cycle through all the rows of the select statement for a callsign       
            row_0 = r   # Just so as to keep the working sections of the original code
            print "Next row is: ", row_0
            # Compute current flight take-off time minus previous flight landing-time
            time_delta = datetime.datetime.strptime(row_0[1], "%H:%M:%S") - datetime.datetime.strptime(prev_stime, "%H:%M:%S")
            delta_secs = time_delta.total_seconds()
            print "Delta secs is: ", delta_secs, " Time limit is: ", lmt_secs
            prev_stime = row_0[3]               # Set previous flight start time to current flight end time used by next iteration
            # if current flight take-off time minus previous flight landing-time is greater than defined limit then different flight
            if (delta_secs) >= lmt_secs: 
                # Flight must be in the next group
                print "----Different flight"
                group += 1 
            else:
                # Flight must be in the same flight group, time difference too small
                print "++++Same flight" 
            cursor.execute('''INSERT INTO flight_group(groupID, sdate, stime, edate, etime, duration, src_callsign, max_altitude, registration, flight_no)
                        VALUES(:groupID,:sdate,:stime,:edate,:etime,:duration,:src_callsign,:max_altitude, :registration, :flight_no)''',
                        {'groupID':group, 'sdate':row_0[0], 'stime':row_0[1], 'edate': row_0[2], 'etime':row_0[3],
                        'duration': row_0[4], 'src_callsign':row_0[5], 'max_altitude':row_0[6], 'registration': row_0[7], 'flight_no': row_0[8]})
            print "GroupID: ", group, " record created ", row_0, "Delta_secs: ", delta_secs 
    db.commit()
    print "-------Phase 2 End-------"
    #    
    #-----------------------------------------------------------------
    # Phase 3 processing   
    #
    # This sums the flight durations for each of the flight groups
    # hence resulting in the actual flight start, end times and duration
    #
    # As well as summing the flight time in a group it must concatenate the track data
    # for each flight group member to form the single track
    #  
    #-----------------------------------------------------------------
    #
    print "+++++++Phase 3 Start+++++++"
    
    #
    # This function since I can't find a library function that does what I want; dates & times
    # are very confusing in Python!
    #
    def time_add(t1, t2):
        ts = 0
        tm = 0
        th = 0
        t = t1[5] + t2[5]
        if t >= 60:
            ts = t - 60
            tm = int(t / 60)
        else:
            ts = t
        t = t1[4] + t2[4] + tm
        if t >= 60:
            tm = t - 60
            th = int(t / 60)
        else:
            tm = t
        th = t1[3] + t2[3] + th
        print "Time tuple is: ", (th, tm, ts)
        tstring = "%s:%s:%s" % (th, tm, ts)
        print "tstring is: ", tstring
        time_return = time.strptime(tstring, "%H:%M:%S")
        return time_return
        
    if group <> 0:    
#       max_groupID = group - 1   
        max_groupID = group 
        print "Max groupID is: ", max_groupID
    else:
        print "No groups to process"
        print "Done"
        return
    
    i = 1
    while i <= max_groupID:
        #
        # 20161005. Changed "<" to "<=", groupID values include max_groupID
        
        cursor.execute('''SELECT max(max_altitude) FROM flight_group WHERE groupID=? ''', (i,))
        r = cursor.fetchone()
        max_altitude = r[0]
        print "Max altitude from group: ", i, " is: ", r[0]

#
# New way of doing it
#          
        # A multi row group can have a total flight time, where flight time is the
        # sum of the row durations, less than the difference between the start and end time of the group
        # since landing and takeoff times less the 2min (say) are being counted as a single flight.
        # It can be argued that the actual flight time should be the difference between the group start and
        # end times, if it isn't the final data will seem to have errors.
        # Hence check for a multi row group and if yes then use max(etime) - min(stime).
        # Good news is the summation code can be removed!
        # But note the old and new ways give slightly different result.  This is because the old way doesn't include
        # the time period between the flights in the group but the new way does.
        # Do:
        # rows = cursor.fetchall()
        # row_count = len(cursor.fetchall())
        # if row_count > 1:
        # cursor.execute('''SELECT min(stime), max(etime) FROM flight_group WHERE groupID=? ''', (i,))
        # row = cursor.fetchone()
        # total_duration = row[1] - row[0]
        # But beware of the subtaction being ok and getting the time in the right format in the end
        
        cursor.execute('''SELECT sdate, stime, edate, etime, duration, src_callsign, max_altitude, registration
                     FROM flight_group WHERE groupID=?
                     ORDER BY sdate, stime ''', (i,))
        rows = cursor.fetchall()
        row_count = len(rows)
        if row_count > 1:
            # Multi row group
            print "Multi row group size for flight group: ", i, " is: ", row_count
        else:
            # Single row group, ie single flight
            print "Single row group size: ", row_count, " Flight group: ", i
        
        cursor.execute('''SELECT min(stime), max(etime) FROM flight_group WHERE groupID=?''', (i,))
        times = cursor.fetchone()           # times is a tuple
#        try: 
#            print "Start new total duration calculation"
#            cursor.execute('''SELECT duration from flight_group WHERE groupID=?''', (i,))
#            durations = cursor.fetchall()
#            d0 = datetime.datetime.strptime("0:0:0", "%H:%M:%S")
#            nduration = datetime.timedelta(hours=d0.hour, minutes=d0.minute, seconds=d0.second)
#            print "durations is: ", durations, " nduration is: ", nduration, " or: ", str(nduration)  
#            t_d1 = datetime.datetime.strptime(TIME_DELTA.replace(" ", ""), "%H:%M:%S")
#            dt1 = datetime.timedelta(hours=t_d1.hour, minutes=t_d1.minute, seconds=t_d1.second)
#            print "t_d1 is: ", t_d1, " dt1 is: ", str(dt1)
            
#            for s in durations:
#                print "S is:", s, " s[0] is: ", s[0]
#                t_d2 = datetime.datetime.strptime(s[0].replace(" ", ""), "%H:%M:%S")
#                dt2 = datetime.timedelta(hours=t_d2.hour, minutes=t_d2.minute, seconds=t_d2.second)
#                print "dt2 is: ", dt2, " or: ", str(dt2)
#                if dt2 > dt1 :
#                    nduration += dt2 
#                    print "nduration is now: ", nduration, " or: ", str(nduration)           
#            print "New total duration calculation is: ", str(nduration)
#        except:
#            print "New duration calc FAILED"
#            
#        total_duration = str(nduration)                 # Was a time delta type, convert to string
#        print "New method total duration is: ", total_duration
        
        print "Value of times are: ", times, " for flight group: ", i
        if times <> (None, None):
            nstime = datetime.datetime.strptime("1900/01/01 " + times[0], '%Y/%m/%d %H:%M:%S')
            netime = datetime.datetime.strptime("1900/01/01 " + times[1], '%Y/%m/%d %H:%M:%S')  
#            print "nstime is: ", nstime, " netime is: ", netime  
            duration = str(netime - nstime)
            print "subtract ok for: ", netime, " from: ", nstime, " Duration is: ", duration
            total_duration = duration  # Just for now    
            # Each set of group records has same value for sdate, edate, callsign and registration 
            try:              
                cursor.execute('''SELECT DISTINCT sdate, edate, src_callsign, registration FROM flight_group WHERE groupID=?''', (i,))
                data = cursor.fetchone()
                print "Flight results for group: ", i, " is: ", data
                sdate = data[0]
                edate = data[1]
                callsign = data[2]
                registration = data[3]
            except:
                print "Group data selection failed"
        else:
            print "No rows in Flight_group"
            # Can this happen, a group with no flights? Check
            i += 1
            continue

        #
        # Concatenate the tracks for each flight group into one track into table trackFinal, 
        # (Note the track table could then be deleted) 
        #
        print "Start concatentate tracks for group: ", i
        cursor.execute('''SELECT flight_no, sdate, stime FROM flight_group WHERE groupID=? ORDER BY sdate, stime ''', (i,))        
        rows = cursor.fetchall()
        print "Group flight rows are: ", rows 
        this_flight_no = rows[0][0]  # Use the first flight number of the group 
        print "this_flight_no is: ", this_flight_no
        track_no = 0  # Set track_no to zero and increment for each track added for each flight in the group 
        for flight in rows:
            print "Concatenate tracks for Flight: ", flight
            cursor.execute('''SELECT id, flight_no, track_no, latitude, longitude, altitude, course, speed, timeStamp FROM track WHERE flight_no=? ORDER BY timeStamp''', (flight[0],))
            tracks = cursor.fetchall()
            for track in tracks:
                track_no += 1
                latitude = track[3]
                longitude = track[4]
                altitude = track[5]
                course = track[6]
                speed = track[7]
                timeStamp = track[8]
#                print "Add to TrackFinal track no: ", track_no
                addFinalTrack(cursor, this_flight_no, track_no, longitude, latitude, altitude, course, speed, timeStamp, settings)
        print "End concatenate tracks for group: ", i     
        
        cursor.execute('''SELECT min(stime), max(etime), registration, min(flight_no) FROM flight_group WHERE groupID=? ''', (i,))      
        r = cursor.fetchone()
        print "Start time is: ", r[0], " End time is: ", r[1], " Duration is: ", total_duration, " Registration is: ", r[2], " Flight_no is: ", r[3], " groupID: ", i
        cursor.execute('''INSERT INTO flights(sdate, stime, edate, etime, duration, src_callsign, max_altitude, registration, flight_no)
                                    VALUES(:sdate,:stime,:edate,:etime,:duration,:src_callsign,:max_altitude, :registration, :flight_no)''',
                                    {'sdate':sdate, 'stime':r[0], 'edate': edate, 'etime':r[1],
                                    'duration': total_duration, 'src_callsign':callsign, 'max_altitude':max_altitude, 'registration':r[2], 'flight_no':r[3]})  
        db.commit()
        i = i + 1
        print "*****Flight logged to flights*********"
    print "-------Phase 3 End--------"
    return
    
        
        
    
