# This module is an API to create a gpx format file from data supplied

#Example of simple gpx track file
#
# Track files, ie .gpx files can be viewed with http://www.mygpsfiles.com/app/.
# Note is is possible with this web site to upload a single file or a group of files
#
#See: http://cycleseven.org/gps-waypoints-routes-and-tracks-the-difference
#
#.gpx Track

#<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
#<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1" creator="RouteConverter">
#    <metadata>
#        <name>Test file by Patrick</name>
#    </metadata>
#    <trk>
#        <name>Patrick's Track</name>
#        <trkseg>
#            <trkpt lon="9.860624216140083" lat="54.9328621088893">
#                <ele>0.0</ele>
#                <name>Position 1</name>
#            </trkpt>
#            <trkpt lon="9.86092208681491" lat="54.93293237320851">
#                <ele>0.0</ele>
#                <name>Position 2</name>
#            </trkpt>
#            <trkpt lon="9.86187816543752" lat="54.93327743521187">
#                <ele>0.0</ele>
#                <name>Position 3</name>
#            </trkpt>
#            <trkpt lon="9.862439849679859" lat="54.93342326167919">
#                <ele>0.0</ele>
#                <name>Position 4</name>
#            </trkpt>
#        </trkseg>
#    </trk>
#</gpx>

#from time import *

class gpxTrack:
#    def __init__(self, TrackNo, TrackFile, TrackName):
    def __init__(self, TrackNo, TrackFile, TrackName, Sdate, Stime, Duration, Registration, MaxAltitude):
        # Add: sdate, stime, duration, registration
        self.TrackNo = "OGN Track No:%d" % (TrackNo)
        self.TrackFile = TrackFile
        trackStart = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<gpx xmlns=\"http://www.topografix.com/GPX/1/1\" version=\"1.1\" creator=\"OGN Flogger\">\n\t<metadata>\n\t\t<name>OGN Flogger Track</name>\n\t</metadata>\n\t<trk>\n\t\t<name>" + self.TrackNo + "</name>\n"
#        trackStart = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<gpx xmlns=\"http://www.topografix.com/GPX/1/1\" version=\"1.1\" creator=\"OGN Flogger\">\n\t<metadata>\n\t\t<name>OGN Flogger Track</name>\n\t</metadata>\n\t<trk>\n\t\t<name>" + self.TrackNo + "</name>\n"
        trackStart = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<gpx xmlns=\"http://www.topografix.com/GPX/1/1\" version=\"1.1\" creator=\"OGN Flogger\">\n\t<metadata>\n\t\t<name>OGN Flogger Track. Date: " + Sdate + " Time: " + Stime + " Duration: " + Duration + " Registration: " + Registration + "</name>\n\t</metadata>\n\t<trk>\n\t\t<name>" + self.TrackNo + "</name>\n"
#        print "gpx XML is: " + trackStart
        self.track = open (TrackFile, 'w')
        self.track.write(trackStart)
        print "New gpxTrack object"
      
    def AddTrackSeg(self, trackName):
        self.trackName = trackName
        self.positionNos = 0                                     # Initialise position name number
        trackSegStart = "\t\t<trkseg>\n" 
        self.track.write(trackSegStart)
                                           
        
    def EndTrackSeg(self):
        self.trackSegEnd = "\t\t</trkseg>\n"
        self.track.write(self.trackSegEnd)
        
    def AddTrackPnt(self, longitude, latitude, elevation, timeStamp):
        self.longitude = longitude
        self.latitude = latitude
        self.elevation = elevation
        self.positionNos = self.positionNos + 1                       # Compute next position name number
        self.positionName = "Position %d" % (self.positionNos)   # Form next positionName string
        self.timeStamp = timeStamp
#        self.trackpnt = "\t\t\t<trkpt lon=\"" + str(self.longitude) + "\" lat=\"" + str(self.latitude) + "\">\n" + "\t\t\t\t<ele>" + str(self.elevation) + "</ele>\n\t\t\t\t<time>" + self.timeStamp + "</time>\n\t\t\t\t<name>" + self.positionName + "</name>\n\t\t\t</trkpt>\n"
        #self.trackpnt = "\t\t\t<trkpt lon=\"" + str(self.longitude) + "\" lat=\"" + str(self.latitude) + "\">\n" + "\t\t\t\t<ele>" + str(self.elevation) + "</ele>\n\t\t\t\t<name>" + self.positionName + "</name>\n\t\t\t</trkpt>\n"
#        self.trackpnt = "\t\t\t<trkpt lat=\"" + str(self.latitude) + "\" lon=\"" + str(self.longitude) + "\">\n" + "\t\t\t\t<ele>" + str(self.elevation) + "</ele>\n\t\t\t\t<name>" + self.positionName + "</name>\n\t\t\t</trkpt>\n"
        
        self.trackpnt = "\t\t\t<trkpt lon=\"%s\" lat=\"%s\">\n\t\t\t\t<ele>%s</ele>\n\t\t\t\t<time>%s</time>\n\t\t\t\t<name>%s</name>\n\t\t\t</trkpt>\n" % (str(self.longitude), str(self.latitude), str(self.elevation), self.timeStamp, self.positionName)

        self.track.write(self.trackpnt)
        
    def EndTrack (self):
       self.trackEnd = "\t</trk>\n</gpx>\n"
       self.track.write(self.trackEnd)
       self.track.close()
"""      
track1 = gpxTrack(1, "track.gpx", "test", "1","2","3","4", "5")
track1.AddTrackSeg("Track1")
track1.AddTrackPnt(1,10,100,"1000")
track1.AddTrackPnt(2,20,200,"2000")
track1.EndTrackSeg()
track1.EndTrack()
"""
"""
track2 = gpxTrack(2, "track2.gpx", "test2")
track2.AddTrackSeg("Track1")
track2.AddTrackPnt(9.860624216140083,54.9328621088893,200.0)
track2.AddTrackPnt(2,20,200)
track2.EndTrackSeg()
track2.EndTrack()
"""
   