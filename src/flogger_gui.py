#import sys
#import os
#import string
from PyQt4 import QtGui, QtCore, uic
from PyQt4.Qt import SIGNAL
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#import subprocess
from parse import *
#from ConfigParser import *
from configobj import ConfigObj
#import src.flogger3
#import src.flogger_resources_rc
from flogger3 import *
from flogger_settings import * 
from LatLon import *
import gpxpy
import matplotlib.pyplot as plt
import mplleaflet
#from flogger_splash import *
from flogger_moviesplash import *
from importlib import import_module
import time
from flogger_path_join import *

from flogger_get_coords import get_coords




#
# Add Main def for packaging. 20180507
#

# 20170311 
# get the directory of this script
print "Module start"
path = os.path.dirname(os.path.abspath(__file__))
#path = "/home/pjr/git_neon.2/OGN-Flight-Logger_V3.2"
print "Current path is: ", path
try:
    print "Directory name: ", path
    pyrcc4_cmd = "pyrcc4 -o "
#    pyrcc4_out = os.path.join(path,"flogger_resources_rc.py")
    pyrcc4_out = path_join(path, ["flogger_resources_rc.py"])
#    pyrcc4_in = os.path.join(path,"../data/flogger_resources.qrc")
#    pyrcc4_in = os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), "data"), "flogger_resources.qrc")
#    p1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
#    print "p1: ", p1
#    pyrcc4_in = path_join(p1, ["data", "flogger_resources.qrc"])
    pyrcc4_in = path_join_dd(os.path.abspath(__file__), ["data", "flogger_resources.qrc"])
    
#    pyrcc4_in = path_join((os.path.dirname(os.path.abspath(__file__)), os.pardir), ["data", "flogger_resources.qrc"])
    print "pyrcc4_in: ", pyrcc4_in
    print "pyrcc4_out: ", pyrcc4_out
    pyrcc4_cmd = "pyrcc4 -o %s %s" % (pyrcc4_out, pyrcc4_in)
    os.system(pyrcc4_cmd)
    print "pyrcc4 ran ok"
    try:
        resources_rc_path = os.path.join(path, "../data/flogger_resources_rc")
        print "resources_rc_path: ", resources_rc_path
    except:
        print "Dynamic import failed"                         # pyrcc4 makes the file, then it can be imported
    print "PyQt4 flogger_resources_rc.py built and imported-1"
except:
    print "failed to compile resources"
    exit()
#Ui_MainWindow, base_class = uic.loadUiType(os.path.join(path,"flogger.ui"))
#Ui_AboutWindow, base_class = uic.loadUiType(os.path.join(path,"flogger_about.ui"))
#Ui_HelpWindow, base_class = uic.loadUiType(os.path.join(path,"flogger_help.ui"))
#path_join_dd(os.path.abspath(__file__), ["data", "flogger_ui"])
#path_join_dd(os.path.abspath(__file__), ["data", "flogger_about.ui"])
#path_join_dd(os.path.abspath(__file__), ["data", "flogger_help.ui"])
print "Setup Ui_Window"
#Ui_MainWindow, base_class = uic.loadUiType(os.path.join(path,"../data/flogger.ui"))
#Ui_AboutWindow, base_class = uic.loadUiType(os.path.join(path,"../data/flogger_about.ui"))
#Ui_HelpWindow, base_class = uic.loadUiType(os.path.join(path,"../data/flogger_help.ui"))



Ui_MainWindow, base_class = uic.loadUiType(path_join_dd(os.path.abspath(__file__), ["data", "flogger.ui"]))
Ui_AboutWindow, base_class = uic.loadUiType(path_join_dd(os.path.abspath(__file__), ["data", "flogger_about.ui"]))
Ui_HelpWindow, base_class = uic.loadUiType(path_join_dd(os.path.abspath(__file__), ["data", "flogger_help.ui"]))
print "Ui_Windows setup"
    
def main(): 
    print "start main" 
    app = QtGui.QApplication(sys.argv)
    path = os.path.dirname(os.path.abspath(__file__))
	# Create and display the splash screen
#    splash_pix = QPixmap(os.path.join(path,"../data/flogger_icon-03.png"))
#    splash_pix = QPixmap(path_join_dd(os.path.abspath(__file__),["data", "flogger_icon-03.png"]))
#    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)

#    movie = QMovie(os.path.join(path,"../data/ogn-logo-ani.gif"))
    movie = QMovie(path_join_dd(os.path.abspath(__file__),["data", "ogn-logo-ani.gif"]))

    splash = MovieSplashScreen(movie)
    splash.show()
    
    start = time.time()
    
    i = 0    
    while movie.state() == QMovie.Running and time.time() < start + 5:
        app.processEvents()
    # 
    # This section takes time to run building the ui and resources files from flogger.ui 
    #
    
#    try:
#        print "Build UI resource files start"
#        pyrcc4_cmd = "pyrcc4 -o "
#        pyrcc4_out = os.path.join(path,"flogger_resources_rc.py")
#        pyrcc4_in = os.path.join(path,"../data/flogger_resources.qrc")
#        pyrcc4_cmd = "pyrcc4 -o %s %s" % (pyrcc4_out, pyrcc4_in)
#        os.system(pyrcc4_cmd)
#        print "Build UI resource files end"
#        time.sleep(5)
#    except:
#        print "failed to compile resources"
#        exit()
        
        
    print "Call MyApp"
    window = MyApp()
    print "Call window.show()"
    window.show()

    splash.finish(window)
    
    print "Splash screen end"
    sys.exit(app.exec_())


class AboutWindow(QtGui.QMainWindow, Ui_AboutWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)
        # Only one button - Ok
        self.OkpushButton.clicked.connect(self.floggerOkpushButton)
        return
    
    def floggerOkpushButton(self):
        print "About Ok button clicked"
        self.close()
        return
    
class HelpWindow(QtGui.QMainWindow, Ui_HelpWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)
        # Only one button - Ok
        self.HelppushButton.clicked.connect(self.floggerHelppushButton)
        return
    
    def floggerHelppushButton(self):
        print "Help Ok button clicked"
        self.close()
        return
    

#global settings_file_dot_txt

#class Window (QtGui.QMainWindow, form_class):
class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        print "init MyApp"
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
#        Ui_AboutWindow.__init__(self)
        
        
#        self.Iconlabel.setPixmap(pixmap)
#        self.iconlabel.show()
        self.show()
        
        
        self.setupUi(self)
        global settings
        settings = class_settings()
        
        self.actionAbout.triggered.connect(self.AboutButton)
        self.actionHelp_2.triggered.connect(self.HelpButton)

        
#        self.RunningLabel.setText("Stopped")
#        self.iconpath = os.path.join(path, "../data/flogger_icon-08.png")
        self.iconpath = path_join_dd(os.path.abspath(__file__),["data", "flogger_icon-08.png"])
        print "Icon path: ", self.iconpath
        self.setWindowIcon(QtGui.QIcon(self.iconpath))
        self.pixmap = QPixmap(self.iconpath)
        self.Iconlabel.setPixmap(self.pixmap) 
        
        self.actionStart.triggered.connect(self.floggerStart)  
        self.actionStop.triggered.connect(self.floggerStop)  
        self.actionQuit.triggered.connect(self.floggerQuit)  
        self.FleetCheckRadioButton.toggled.connect(self.floggerFleetCheckRadioButton) 
        self.RecordTracksRadioButton.toggled.connect(self.floggerRecordTracksRadioButton)  
        self.TakeoffEmailButton.toggled.connect(self.floggerTakeoffEmailButton)  
        self.LandingEmailButton.toggled.connect(self.floggerLandingEmailButton)  
        self.LaunchFailuresButton.toggled.connect(self.floggerLaunchFailuresButton)
        self.LogTugsButton.toggled.connect(self.floggerLogTugsButton)
        self.IGCFormatButton.toggled.connect(self.floggerIGCFormatButton)  
        self.LiveTestButton.toggled.connect(self.floggerLiveTestButton)
        
        
        self.UpdateButton.clicked.connect(self.floggerUpdateConfig)
        self.CancelButton.clicked.connect(self.floggerCancelConfigUpdate)
        
        self.Add2FleetOkButton.clicked.connect(self.floggerAdd2FleetOkButton)
        self.Add2FleetCancelButton.clicked.connect(self.floggerAdd2FleetCancelButton)
        
        self.DelFromFleetOkButton.clicked.connect(self.floggerDelFromFleetOkButton)
        self.RunningLabel.setStyleSheet("color: red")  
        
        self.FlightLogcalendar.clicked.connect(self.floggerFlightLog)
        self.IncludeTugsButton.toggled.connect(self.floggerIncludeTugsButton)
        self.FlightLogTable.doubleClicked.connect(self.floggerFlightLogDoubleClicked)
        self.FlightLogTable.verticalHeader().sectionClicked.connect(self.floggerFlightLogDoubleClicked)  
        self.FlightLogTable.setColumnHidden(10, True)


        
        
        # Initialise values from config file

#        filepath = os.path.join(path, "flogger_settings.py")
        filepath = os.path.join(path, "flogger_settings_file.txt")

#        filename = open(filepath)
        try:
#            self.config = ConfigObj("flogger_settings_file.txt", raise_errors = True)
            settings_file_dot_txt = path_join_dd(os.path.abspath(__file__), ["data", "flogger_settings_file.txt"])
            self.config = ConfigObj(settings_file_dot_txt, raise_errors = True)
#            self.config = ConfigObj("../data/flogger_settings_file.txt", raise_errors = True)
            print "Opened flogger_settings_file.txt path:", settings_file_dot_txt
        except:
            print "Open failed"
            print self.config
            
#
# This section reads all the values from the config file and outputs these in the gui fields.
# It also initialises the corresponding settings object config fields. If the values are changed
# in the gui they must be saved in the config file and used as the current values in the settings object
#          
        old_val = self.getOldValue(self.config, "FLOGGER_AIRFIELD_NAME")
        settings.FLOGGER_AIRFIELD_NAME = old_val
#        print settings.FLOGGER_AIRFIELD_NAME
        self.AirfieldBase.setText(old_val)
         
        old_val = self.getOldValue(self.config, "APRS_USER")
        settings.APRS_USER = old_val
        self.APRSUser.setText(old_val)
        
        old_val = self.getOldValue(self.config, "APRS_PASSCODE")    # This might get parsed as an int - need to watch it!
        settings.APRS_PASSCODE = old_val
        self.APRSPasscode.setText(old_val)
        
        old_val = self.getOldValue(self.config, "APRS_SERVER_HOST")    
        settings.APRS_SERVER_HOST = old_val
        self.APRSServerHostName.setText(old_val)
        
        old_val = self.getOldValue(self.config, "APRS_SERVER_PORT")    # This might get parsed as an int - need to watch it!
        settings.APRS_SERVER_PORT = int(old_val)
        self.APRSServerPort.setText(old_val)
        
        old_val = self.getOldValue(self.config, "FLOGGER_RAD")    # This might get parsed as an int - need to watch it!
        settings.FLOGGER_RAD = int(old_val)
        self.AirfieldFlarmRadius.setText(old_val)
         
        old_val = self.getOldValue(self.config, "FLOGGER_AIRFIELD_LIMIT")    # This might get parsed as an int - need to watch it!
        settings.FLOGGER_AIRFIELD_LIMIT = int(old_val)
        self.LandOutRadius.setText(old_val)
        
        old_val = self.getOldValue(self.config, "FLOGGER_AIRFIELD_DETAILS")    
        settings.FLOGGER_AIRFIELD_DETAILS = old_val
        self.AirfieldDetails.setText(old_val)
          
        old_val = self.getOldValue(self.config, "FLOGGER_QFE_MIN")    
        settings.FLOGGER_QFE_MIN = int(old_val)
        self.MinFlightQFE.setText(old_val)
        
        old_val = self.getOldValue(self.config, "FLOGGER_MIN_FLIGHT_TIME")    
        settings.FLOGGER_MIN_FLIGHT_TIME = old_val
        self.MinFlightTime.setText(old_val)
        
        
        old_val = self.getOldValue(self.config, "FLOGGER_V_TAKEOFF_MIN")    
        settings.FLOGGER_V_TAKEOFF_MIN = old_val
        self.MinFlightTakeoffVelocity.setText(old_val)
            
        old_val = self.getOldValue(self.config, "FLOGGER_V_LANDING_MIN")    
        settings.FLOGGER_V_LANDING_MIN = old_val
        self.MinFlightLandingVelocity.setText(old_val) 
                   
        old_val = self.getOldValue(self.config, "FLOGGER_DT_TUG_LAUNCH")    
        settings.FLOGGER_DT_TUG_LAUNCH = old_val
        self.MinTugLaunchTIme.setText(old_val)
#
# Note this could be done using LatLon
#        
        old_val_lat = self.getOldValue(self.config, "FLOGGER_LATITUDE")    # This might get parsed as a real - need to watch it!
        print "Old_val: " + old_val_lat
        settings.FLOGGER_LATITUDE = old_val_lat
        
        old_val_lon = self.getOldValue(self.config, "FLOGGER_LONGITUDE")    # This might get parsed as a real - need to watch it!
        print "Old_lon: " + old_val_lon
        settings.FLOGGER_LONGITUDE = old_val_lon
#        self.AirfieldLongitude.setText(old_val_lon)
        
        old_latlon = LatLon(Latitude( old_val_lat), Longitude(old_val_lon))
        old_latlonstr = old_latlon.to_string('D% %H')
        self.AirfieldLatitude.setText(old_latlonstr[0])
        self.AirfieldLongitude.setText(old_latlonstr[1])
               
        old_val = self.getOldValue(self.config, "FLOGGER_FLEET_CHECK")
        print "Fleet Check: " + old_val 
        if old_val == "Y":
            print "Y"
            self.FleetCheckRadioButton.setChecked(True)
        else:
            print "N"   
            self.FleetCheckRadioButton.setChecked(False)
        settings.FLOGGER_FLEET_CHECK = old_val
                          
        old_val = self.getOldValue(self.config, "FLOGGER_LOG_TUGS")
        print "Log Tugs Button: ", old_val 
        if old_val == "Y":
            print "Y"
            self.LogTugsButton.setChecked(True)
        else:
            print "N"   
            self.LogTugsButton.setChecked(False)
        settings.FLOGGER_FLEET_CHECK = old_val
        
        old_val = self.getOldValue(self.config, "FLOGGER_TRACKS")
        print "Record Tracks: " + old_val 
        if old_val == "Y":
            print "Y"
            self.RecordTracksRadioButton.setChecked(True)
        else:
            print "N"   
        settings.FLOGGER_TRACKS = old_val 
                     
        old_val = self.getOldValue(self.config, "FLOGGER_TAKEOFF_EMAIL")
        print "Email takeoffs is: " + old_val 
        if old_val == "Y":
            print "Y"
            self.TakeoffEmailButton.setChecked(True)
        else:
            print "N"   
        settings.FLOGGER_TAKEOFF_EMAIL = old_val 
        
                             
        old_val = self.getOldValue(self.config, "FLOGGER_LANDING_EMAIL")
        print "Email landings is: " + old_val 
        if old_val == "Y":
            print "Y"
            self.LandingEmailButton.setChecked(True)
        else:
            print "N"   
        settings.FLOGGER_LANDING_EMAIL = old_val 
        
        old_val = self.getOldValue(self.config, "FLOGGER_DB_SCHEMA")    
        settings.FLOGGER_DB_SCHEMA = old_val
        self.DBSchemaFile.setText(old_val)
        settings.FLOGGER_DB_SCHEMA = old_val
        
        
        old_val = self.getOldValue(self.config, "FLOGGER_DB_NAME")    
        settings.FLOGGER_DB_NAME = old_val
        self.DBName.setText(old_val)
        settings.FLOGGER_DB_NAME = old_val    
        
        old_val = self.getOldValue(self.config, "FLOGGER_FLARMNET_DB_URL")    
        settings.FLOGGER_FLARMNET_DB_URL = old_val
        self.FlarmnetURL.setText(old_val)
#        settings.FLOGGER_FLARMNET_DB_URL = old_val
       
        old_val = self.getOldValue(self.config, "FLOGGER_OGN_DB_URL")    
        settings.FLOGGER_OGN_DB_URL = old_val
        self.OGNURL.setText(old_val)
#       settings.FLOGGER_OGN_DB_URL = old_val
                
        old_val = self.getOldValue(self.config, "FLOGGER_KEEPALIVE_TIME")    
        settings.FLOGGER_KEEPALIVE_TIME = int(old_val)
        self.APRSKeepAliveTIme.setText(old_val)

        old_val = self.getOldValue(self.config, "FLOGGER_SMTP_SERVER_URL")  
        print "Initialise FLOGGER_SMTP_SERVER_URL"  
        settings.FLOGGER_SMTP_SERVER_URL = old_val
        self.SMTPServerURL.setText(old_val)
        settings.FLOGGER_SMTP_SERVER_URL = old_val
        print "settings.FLOGGER_SMTP_SERVER_URL: ", settings.FLOGGER_SMTP_SERVER_URL
        
        old_val = self.getOldValue(self.config, "FLOGGER_SMTP_SERVER_PORT")    
        settings.FLOGGER_SMTP_SERVER_PORT = int(old_val)
        self.SMTPServerPort.setText(old_val)
        settings.FLOGGER_SMTP_SERVER_PORT = int(old_val)
        
                
        old_val = self.getOldValue(self.config, "FLOGGER_SMTP_TX") 
        print "TX from file: ", old_val   
        settings.FLOGGER_SMTP_TX = old_val
        self.EmailSenderTX.setText(old_val)
        settings.FLOGGER_SMTP_TX = old_val     
                
        old_val = self.getOldValue(self.config, "FLOGGER_SMTP_RX")    
        settings.FLOGGER_SMTP_RX = old_val
        self.EmailReceiverRX.setText(old_val)
        settings.FLOGGER_SMTP_RX = old_val
                
        old_val = self.getOldValue(self.config, "FLOGGER_APRS_BASES")
        i = 1
        for item in old_val:
#            print "APRS Base: " + item
            if i == 1:
                self.APRSBase1Edit.setText(item)
                i += 1
                continue
            if i == 2:
                self.APRSBase2Edit.setText(item)
                i += 1
                continue
            if i == 3:
                self.APRSBase3Edit.setText(item)
                i += 1
                continue
            if i == 4:
                self.APRSBase4Edit.setText(item)
                i += 1
                continue 
            if i == 5:
                self.APRSBase5Edit.setText(item)
                i += 1
                continue 
            if i == 6:
                self.APRSBase6Edit.setText(item)
                i += 1
                continue 
        settings.FLOGGER_APRS_BASES = old_val
#        print "APRS_BASES: ", old_val
        print "APRS_BASES: ", settings.FLOGGER_APRS_BASES
        
        old_val = self.getOldValue(self.config, "FLOGGER_FLEET_LIST") 
 #       print "FLOGGER_FLEET_LIST: ", old_val 
        for key in old_val.keys():
            # Convert string form of value to int
            old_val[key] = int(old_val[key])
#            print "Key: ", key, " = ", int(old_val[key])
        settings.FLOGGER_FLEET_LIST = old_val
        print "FLOGGER_FLEET_LIST: ", settings.FLOGGER_FLEET_LIST
        
        rowPosition = self.FleetListTable.rowCount()
        for registration in settings.FLOGGER_FLEET_LIST:
            print "rowPosition: ", rowPosition, " Registration: ", registration, " Code: ", settings.FLOGGER_FLEET_LIST[registration]
            self.FleetListTable.insertRow(rowPosition)
            self.FleetListTable.setItem(rowPosition , 0, QtGui.QTableWidgetItem(registration))
            self.FleetListTable.setItem(rowPosition , 1, QtGui.QTableWidgetItem(str(settings.FLOGGER_FLEET_LIST[registration])))
            rowPosition = rowPosition + 1
        
        
        old_val = self.getOldValue(self.config, "FLOGGER_DATA_RETENTION")    # This might get parsed as an int - need to watch it!
        settings.FLOGGER_DATA_RETENTION = int(old_val)
        self.DataRetentionTime.setText(old_val)
          
        old_val = self.getOldValue(self.config, "FLOGGER_LOG_TIME_DELTA")    # This might get parsed as an int - need to watch it!
        settings.FLOGGER_LOG_TIME_DELTA = int(old_val)
        self.LogTimeDelta.setText(old_val) 
                 
        old_val = self.getOldValue(self.config, "FLOGGER_LOCATION_HORIZON")    # This might get parsed as an int - need to watch it!
        settings.FLOGGER_LOCATION_HORIZON = old_val
        self.HorizonAdjustment.setText(old_val)   
                      
        old_val = self.getOldValue(self.config, "FLOGGER_DUPLICATE_FLIGHT_DELTA_T")    
        settings.FLOGGER_DUPLICATE_FLIGHT_DELTA_T = old_val
        self.MinFlightDeltaTime.setText(old_val) 
                             
        old_val = self.getOldValue(self.config, "FLOGGER_QNH")    
#        settings.FLOGGER_QNH = int(old_val)  
        settings.FLOGGER_QNH = old_val
        self.AirfieldQNH.setText(old_val)     
                                     
        old_val = self.getOldValue(self.config, "FLOGGER_FLIGHTS_LOG")    
        settings.FLOGGER_FLIGHTS_LOG = old_val
        self.FlightLogFolder.setText(old_val)  
                                           
        old_val = self.getOldValue(self.config, "FLOGGER_LANDOUT_MODE")    
        settings.FLOGGER_LANDOUT_MODE = old_val
        self.LandoutMsgMode.setText(old_val)
        
        old_val = self.getOldValue(self.config, "FLOGGER_MODE")
        if old_val == "test":
            print "Live/Test mode state is Test"
            self.LiveTestButton.setChecked(True)
                                                       
        old_val = self.getOldValue(self.config, "FLOGGER_INCLUDE_TUG_FLIGHTS")  
        print "Include Tugs Button: " + old_val 
        if old_val == "Y":
            print "Y"
            self.IncludeTugsButton.setChecked(True)
        else:
            print "N"  
        settings.FLOGGER_FLEET_CHECK = old_val
            
            

#
# GUI Initialisation end
#  

#
# Actions Start. Menu Bar
#      
    def floggerStart(self):
        print "flogger start"
        settings.FLOGGER_RUN = True
        flogger = flogger3()
        self.RunningLabel.setStyleSheet("color: green")
        self.RunningLabel.setText("Running...")
#        self.RunningProgressBar.maximum(0)
        self.RunningProgressBar.setProperty("maximum", 0) 
        flogger.flogger_run(settings)
        
        
    def floggerStop(self):
        settings.FLOGGER_RUN = False
        self.RunningLabel.setStyleSheet("color: red")
        self.RunningLabel.setText("Stopped")
        self.RunningProgressBar.setProperty("maximum", 1)
        print "flogger stop"
    
    def floggerQuit(self):
        print "flogger quit"
        
#
# Actions Start, update fields
#

    def floggerUpdateConfig(self):
        print "floggerUpdateConfig called"
        self.floggerAirfieldEdit2(True)
        self.floggerAirfieldDetailsEdit2(True)
        self.floggerAPRSUserEdit2(True)
        self.floggerAPRSPasscodeEdit2(True)
        self.floggerAPRSServerhostEdit2(True)
        self.floggerAPRSServerportEdit2(True)
        self.floggerFlarmRadiusEdit2(True)
        self.floggerLandoutRadiusEdit2(True)
        self.floggerDataRetentionTimeEdit2(True)
        self.floggerAirfieldLatLonEdit2(True)
        self.floggerMinFlightTimeEdit2(True)
        self.floggerMinTakeoffVelocityEdit2(True)
        self.floggerMinLandingVelocityEdit2(True)
        self.floggerMinFlightQFEEdit2(True)
        self.floggerTugLaunchEdit2(True)
        self.floggerKeepAliveTime2(True)
        self.floggerDBSchemaFileEdit2(True)
        self.floggerDBNameEdit2(True)
        self.floggerFlarmnetURL2(True)
        self.floggerOGNURL2(True)
        self.floggerSMTPServerURLEdit2(True)
        self.floggerSMTPServerPortEdit2(True)
        self.floggerEmailSenderEdit2(True)
        self.floggerEmailReceiverEdit2(True)
        self.floggerAPRSBaseEdit2(True)
        self.floggerLogTimeDeltaEdit2(True)
        self.floggerHorizonAdjustmentEdit2(True)
        self.floggerMinFlightDeltaTimeEdit2(True)
        self.floggerMinFlightDeltaTimeEdit2(True)
        self.floggerAirfieldQNHEdit2(True)
        self.floggerFlightLogFolderEdit2(True)
        self.floggerLandoutMsgModeEdit2(True)
#        self.floggerIncludeTugFlightsEdit2(True)
        try:
            self.config.write()
        except:
            print "Writing updated config file, flogger_settings_file.txt FAILED"
        return



    def floggerCancelConfigUpdate(self):
        print "floggerCancelConfigUpdate called"
        self.floggerAirfieldEdit2(False)
        self.floggerAirfieldDetailsEdit2(False)
        self.floggerAPRSUserEdit2(False)
        self.floggerAPRSPasscodeEdit2(False)
        self.floggerAPRSServerhostEdit2(False)
        self.floggerAPRSServerportEdit2(False)
        self.floggerFlarmRadiusEdit2(False)
        self.floggerLandoutRadiusEdit2(False)
        self.floggerDataRetentionTimeEdit2(False)
        self.floggerAirfieldLatLonEdit2(False)
        self.floggerMinFlightTimeEdit2(False)
        self.floggerMinTakeoffVelocityEdit2(False)
        self.floggerMinLandingVelocityEdit2(False)
        self.floggerMinFlightQFEEdit2(False)
        self.floggerTugLaunchEdit2(False)
        self.floggerKeepAliveTime2(False)
        self.floggerDBSchemaFileEdit2(False)
        self.floggerDBNameEdit2(False)
        self.floggerFlarmnetURL2(False)
        self.floggerOGNURL2(False)
        self.floggerSMTPServerURLEdit2(False)
        self.floggerSMTPServerPortEdit2(False)
        self.floggerEmailSenderEdit2(False)
        self.floggerEmailReceiverEdit2(False)
        self.floggerAPRSBaseEdit2(False)
        self.floggerLogTimeDeltaEdit2(False)
        self.floggerHorizonAdjustmentEdit2(False)
        self.floggerMinFlightDeltaTimeEdit2(False)
        self.floggerAirfieldQNHEdit2(False)
        self.floggerFlightLogFolderEdit2(False)
        self.floggerLandoutMsgModeEdit2(False)
#        self.floggerIncludeTugFlightsEdit2(False)
        return
                       
        
    def floggerAirfieldEdit2(self, mode):
        # Mode: True - update all fields, variables to latest values
        
        #       False - restore all fields and variables to values from config (settings.txt) file
        print "Base Airfield button clicked ", "Mode: ", mode 
        if mode:
            # Values have been put into gui field from setting.txt and may then have been changed interactively
            airfield_base = self.AirfieldBase.toPlainText() 
        else:
            # Restore old values from settings.txt
            old_val = self.getOldValue(self.config, "FLOGGER_AIRFIELD_NAME")
#            settings.FLOGGER_AIRFIELD_NAME = old_val
            print settings.FLOGGER_AIRFIELD_NAME
            self.AirfieldBase.setText(old_val)
            print "Airfield Base: " + old_val
            airfield_base = old_val
        # Put current value into settings.txt file for future use
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_AIRFIELD_NAME", airfield_base)
        # Now update python variable to current value in gui and settings.txt
#        self.FLOGGER_AIRFIELD_NAME = airfield_base
#        settings.FLOGGER_AIRFIELD_NAME = airfield_base
        print "FLOGGER_AIRFIELD_NAME from settings.py: ", settings.FLOGGER_AIRFIELD_NAME
        

        
    def floggerAPRSUserEdit2(self, mode):
        print "APRS User button clicked"
        if mode: 
            APRSUser = self.APRSUser.toPlainText()  
        else:
            old_val = self.getOldValue(self.config, "APRS_USER")
            self.APRSUser.setText(old_val)
            APRSUser = old_val
#       print "Airfield B: " + airfield_base
        self.editConfigField("flogger_settings_file.txt", "APRS_USER", APRSUser)
        self.APRS_USER = APRSUser
        

    def floggerAPRSPasscodeEdit2(self, mode):
            print "APRS Passcode button clicked"
            if mode: 
                APRSPasscode = self.APRSPasscode.toPlainText()  
            else:
                old_val = self.getOldValue(self.config, "APRS_PASSCODE")
                self.APRSPasscode.setText(old_val)
                APRSPasscode = old_val
            self.editConfigField("flogger_settings_file.txt", "APRS_PASSCODE", APRSPasscode)
            self.APRS_PASSCODE = APRSPasscode
            
    
    def floggerAPRSServerhostEdit2(self, mode):
            print "APRS Server Host button clicked"
            if mode: 
                APRSServerhost = self.APRSServerHostName.toPlainText()  
            else:
                old_val = self.getOldValue(self.config, "APRS_SERVER_HOST")
                self.APRSServerHostName.setText(old_val)
                APRSServerhost = old_val
            self.editConfigField("flogger_settings_file.txt", "APRS_SERVER_HOST", APRSServerhost)
            self.APRS_SERVER_HOST = APRSServerhost
            
    
    def floggerAPRSServerportEdit2(self, mode):
            print "APRS Server Port button clicked"
            if mode: 
                APRSServerport = self.APRSServerPort.toPlainText()  
            else:
                old_val = self.getOldValue(self.config, "APRS_SERVER_PORT")
                self.APRSServerPort.setText(old_val)
                APRSServerport = old_val
            self.editConfigField("flogger_settings_file.txt", "APRS_SERVER_PORT", APRSServerport)
            self.APRS_SERVER_PORT = int(APRSServerport)
            
    def floggerDataRetentionTimeEdit2(self, mode): 
            print "Data Retention TIme button clicked"
            if mode: 
                DataRetentionTime = self.DataRetentionTime.toPlainText()  
            else:
                old_val = self.getOldValue(self.config, "FLOGGER_DATA_RETENTION")
                self.DataRetentionTime.setText(old_val)
                DataRetentionTime = old_val
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_DATA_RETENTION", DataRetentionTime)
            self.FLOGGER_DATA_RETENTION = int(DataRetentionTime)
            
    def floggerLogTimeDeltaEdit2(self, mode):    
            print "Log Time Delta button clicked"
            if mode: 
                LogTimeDelta = self.LogTimeDelta.toPlainText()  
            else:
                old_val = self.getOldValue(self.config, "FLOGGER_LOG_TIME_DELTA")
                self.LogTimeDelta.setText(old_val)
                LogTimeDelta = old_val
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_LOG_TIME_DELTA", LogTimeDelta)
            self.FLOGGER_LOG_TIME_DELTA = int(LogTimeDelta)
        
    def floggerHorizonAdjustmentEdit2(self, mode):   
            print "Horizon Adjustment button clicked"
            if mode: 
                HorizonAdjustment = self.HorizonAdjustment.toPlainText()  
            else:
                old_val = self.getOldValue(self.config, "FLOGGER_LOCATION_HORIZON")
                self.HorizonAdjustment.setText(old_val)
                HorizonAdjustment = old_val
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_LOCATION_HORIZON", HorizonAdjustment)
            self.FLOGGER_LOCATION_HORIZON = HorizonAdjustment
            
    def floggerAirfieldQNHEdit2(self, mode):
        print "QNH Setting button clicked"
        if mode: 
            AirfieldQNH = self.AirfieldQNH.toPlainText()  
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_QNH")
            self.AirfieldQNH.setText(old_val)
            AirfieldQNH = old_val
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_QNH", AirfieldQNH)
#        self.FLOGGER_QNH = int(AirfieldQNH)
        self.FLOGGER_QNH = AirfieldQNH
        
    def floggerFlarmRadiusEdit2(self, mode):
            print "Flarm Radius button clicked"
            if mode: 
                FlarmRadius = self.AirfieldFlarmRadius.toPlainText()  
            else:
                old_val = self.getOldValue(self.config, "FLOGGER_RAD")
                self.AirfieldFlarmRadius.setText(old_val)
                FlarmRadius = old_val
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_RAD", FlarmRadius)
            self.FLOGGER_RAD = int(FlarmRadius)
   
    def floggerLandoutRadiusEdit2(self, mode):
            print "Flarm Radius button clicked"
            if mode: 
                LandOutRadius = self.LandOutRadius.toPlainText()  
            else:
                old_val = self.getOldValue(self.config, "FLOGGER_AIRFIELD_LIMIT")
                self.LandOutRadius.setText(old_val)
                LandOutRadius = old_val
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_AIRFIELD_LIMIT", LandOutRadius)
            self.FLOGGER_AIRFIELD_LIMIT = int(LandOutRadius)
        
            
    def floggerAirfieldDetailsEdit2(self, mode):
        #
        # This needs to be changed determine the Lat/Long is AirfieldDetails is supplied
        # and write them back to the form and to settings.py.  Most of the code is similar
        # to that below except the lat/long have to found from the get_coords function
        # in flogger3.py
        #
        print "Airfield Details button clicked. Mode: ", mode
        if mode:
            airfield_details = self.AirfieldDetails.toPlainText()
            print "Airfield Details: ", airfield_details
            if airfield_details <> "":
                loc = get_coords(airfield_details)
                lat = str(loc[0])    # returned as numbers, convert to string
                lon = str(loc[1])    # as above
                qnh = str(loc[2])    # as above    
                self.editConfigField("flogger_settings_file.txt", "FLOGGER_LATITUDE", lat)
                self.editConfigField("flogger_settings_file.txt", "FLOGGER_LONGITUDE", lon)
                self.editConfigField("flogger_settings_file.txt", "FLOGGER_QNH", qnh)
                # The following is just to get Lat & Lon into the right format for display on form
                latlon = LatLon(Latitude(lat), Longitude(lon))
                latlonStr = latlon.to_string('D% %H')
                print "latlonStr: ", latlonStr
                self.AirfieldLatitude.setText(latlonStr[0])
                self.AirfieldLongitude.setText(latlonStr[1])
                self.AirfieldQNH.setText(qnh)
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_AIRFIELD_DETAILS")
            self.AirfieldDetails.setText(old_val)
            airfield_details = old_val
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_AIRFIELD_DETAILS", airfield_details)

    def floggerAirfieldLatLonEdit2(self, mode):
        print "Airfield latitude, longitude called"
        if mode:
            airfieldLat = self.AirfieldLatitude.toPlainText()
            airfieldLon = self.AirfieldLongitude.toPlainText()
            airfieldlatlon = string2latlon(str(airfieldLat), str(airfieldLon), 'D% %H')
            print "Airfield lat/lon: ", airfieldlatlon
            airfieldLatLonStr = airfieldlatlon.to_string("%D")
            print "Update Lat/Lon: ", airfieldLatLonStr
            print "Latlonstr: ", airfieldLatLonStr[0], " :", airfieldLatLonStr[1]
            old_val_lat = airfieldLatLonStr[0]
            old_val_lon = airfieldLatLonStr[1]
        else:
            old_val_lat = self.getOldValue(self.config, "FLOGGER_LATITUDE")
            old_val_lon = self.getOldValue(self.config, "FLOGGER_LONGITUDE")
            print "Old Lat: ", old_val_lat, " Old Lon: ", old_val_lon
            airfieldlatlon = LatLon(Latitude(old_val_lat), Longitude(old_val_lon))
            print "airfieldlatlon: ", airfieldlatlon
            airfieldLatLonStr = airfieldlatlon.to_string('D% %H')
            print "airfieldlatlonStr: ", airfieldLatLonStr
            self.AirfieldLatitude.setText(airfieldLatLonStr[0])
            self.AirfieldLongitude.setText(airfieldLatLonStr[1])
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_LATITUDE", old_val_lat)
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_LONGITUDE", old_val_lon)
        return
                  
    def floggerMinFlightTimeEdit2(self, mode):
        print "Min Flight Time button clicked"
        # Note. Format is "HH:MM:SS" ie a string
        if mode:
            min_flight_time = self.MinFlightTime.toPlainText() 
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_MIN_FLIGHT_TIME")
            self.MinFlightTime.setText(old_val)
            min_flight_time = old_val 
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_MIN_FLIGHT_TIME", min_flight_time) 
        
                  
    def floggerMinTakeoffVelocityEdit2(self, mode):
        print "Min Takeoff Velocity button clicked"
        # Note. Format is "HH:MM:SS" ie a string
        if mode:
            min_takeoff_velocity = self.MinFlightTakeoffVelocity.toPlainText() 
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_V_TAKEOFF_MIN")
            self.MinFlightTakeoffVelocity.setText(old_val)
            min_takeoff_velocity = old_val 
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_V_TAKEOFF_MIN", min_takeoff_velocity) 
        
                  
    def floggerMinLandingVelocityEdit2(self, mode):
        print "Min Landing Velocity button clicked"
        # Note. Format is "HH:MM:SS" ie a string
        if mode:
            min_landing_velocity = self.MinFlightLandingVelocity.toPlainText() 
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_V_LANDING_MIN")
            self.MinFlightLandingVelocity.setText(old_val)
            min_landing_velocity = old_val 
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_V_LANDING_MIN", min_landing_velocity) 
        
                  
    def floggerMinFlightQFEEdit2(self, mode):
        print "Min QFE button clicked"
        # Note. Format is "HH:MM:SS" ie a string
        if mode:
            min_QFE = self.MinFlightQFE.toPlainText() 
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_QFE_MIN")
            self.MinFlightQFE.setText(str(old_val))
            min_QFE = int(old_val) 
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_QFE_MIN", min_QFE) 
        self.FLOGGER_QFE_MIN = min_QFE
                  
    def floggerTugLaunchEdit2(self, mode):
        print "Delta Tug Time button clicked"
        # Note. Format is "HH:MM:SS" ie a string
        if mode:
            min_tug_time = self.MinTugLaunchTIme.toPlainText() 
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_DT_TUG_LAUNCH")
            self.MinTugLaunchTIme.setText(old_val)
            min_tug_time = int(old_val) 
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_DT_TUG_LAUNCH", min_tug_time) 
        self.FLOGGER_DT_TUG_LAUNCH = min_tug_time
    
    def floggerFleetCheckRadioButton(self):
        print "Fleet Check Radio Button clicked" 
        if self.FleetCheckRadioButton.isChecked():
            print "Fleet check checked"
            self.FLOGGER_FLEET_CHECK = "Y"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_FLEET_CHECK", "Y")
        else:
            print "Fleet check unchecked"
            self.FLOGGER_FLEET_CHECK = "N"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_FLEET_CHECK", "N")
         
    def floggerRecordTracksRadioButton(self):
        print "Record Tracks Radio Button clicked" 
        if self.RecordTracksRadioButton.isChecked():
            print "Record Tracks checked"
            self.FLOGGER_TRACKS = "Y"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_TRACKS", "Y")
        else:
            print "Record Tracks unchecked"
            self.FLOGGER_TRACKS = "N"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_TRACKS", "N")  
            
            
    def floggerLiveTestButton(self):
        print "Live | Test Radio Button clicked" 
        if self.LiveTestButton.isChecked():
            print "Live | Test mode checked: Test Mode"
            self.FLOGGER_MODE = "Y"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_MODE", "test")
        else:
            print "Live | Test mode unchecked: Live Mode"
            self.FLOGGER_MODE = "live"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_MODE", "live")  
            
    def floggerTakeoffEmailButton(self):   
        print "Record Takeoff Radio Button clicked" 
        if self.TakeoffEmailButton.isChecked():
            print "Record Takeoff checked"
            self.FLOGGER_TAKEOFF_EMAIL = "Y"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_TAKEOFF_EMAIL", "Y")
        else:
            print "Takeoff Takeoff Button unchecked"
            self.FLOGGER_TAKEOFF_EMAIL = "N"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_TAKEOFF_EMAIL", "N")  
            
    def floggerLandingEmailButton(self): 
        print "Landing Email button clicked" 
        if self.LandingEmailButton.isChecked():
            print "Landing Email button checked"
            self.FLOGGER_TAKEOFF_EMAIL = "Y"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_LANDING_EMAIL", "Y")
        else:
            print "Landing Email button unchecked"
            self.FLOGGER_LANDING_EMAIL = "N"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_LANDING_EMAIL", "N")
            
    def floggerLaunchFailuresButton(self):
        print "Launch Failures button clicked" 
        if self.LaunchFailuresButton.isChecked():
            print "Launch Failures button checked"
            self.FLOGGER_LOG_LAUNCH_FAILURES = "Y"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_LOG_LAUNCH_FAILURES", "Y")
        else:
            print "Launch Failures button unchecked"
            self.FLOGGER_LOG_LAUNCH_FAILURES = "N"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_LOG_LAUNCH_FAILURES", "N")
    
    def floggerLogTugsButton(self):
        print "Log Tugs button clicked" 
        if self.LogTugsButton.isChecked():
            print "Log Tugs button checked"
            self.FLOGGER_LOG_TUGS = "Y"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_LOG_TUGS", "Y")
        else:
            print "Log Tugs button unchecked"
            self.FLOGGER_LOG_TUGS = "N"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_LOG_TUGS", "N")
            
    def floggerIGCFormatButton(self):
        print "IGC Format Button clicked" 
        if self.IGCFormatButton.isChecked():
            print "IGC Format button checked"
            self.FLOGGER_TRACKS_IGC = "Y"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_TRACKS_IGC", "Y")
        else:
            print "IGC Format button unchecked"
            self.FLOGGER_TRACKS_IGC = "N"
            self.editConfigField("flogger_settings_file.txt", "FLOGGER_TRACKS_IGC", "N")
             
    def floggerIncludeTugsButton(self):
        print "Include Tugs Radio Button clicked" 
        if self.IncludeTugsButton.isChecked():
            print "Include Tugs Button checked"
            self.FLOGGER_INCLUDE_TUG_FLIGHTS = "Y"
        else:
            print "Include Tugs Button unchecked"
            self.FLOGGER_INCLUDE_TUG_FLIGHTS = "N"
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_INCLUDE_TUG_FLIGHTS", self.FLOGGER_INCLUDE_TUG_FLIGHTS)
        
            
    def floggerKeepAliveTime2(self, mode):
        print "Keep Alive Time button clicked" 
        if mode:
            keep_alive_time = self.APRSKeepAliveTIme.toPlainText() 
        else: 
            old_val = self.getOldValue(self.config, "FLOGGER_KEEPALIVE_TIME") 
            self.APRSKeepAliveTIme.setText(old_val)
            keep_alive_time = old_val
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_KEEPALIVE_TIME", keep_alive_time)
        self.FLOGGER_KEEPALIVE_TIME = keep_alive_time 
            
    def floggerDBSchemaFileEdit2(self, mode):
        print "DB Schema File button clicked"
        if mode: 
            db_schema_file = self.DBSchemaFile.toPlainText() 
        else: 
            old_val = self.getOldValue(self.config, "FLOGGER_DB_SCHEMA")
            self.DBSchemaFile.setText(old_val)
            db_schema_file = old_val 
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_DB_SCHEMA", db_schema_file) 
        self.FLOGGER_DB_SCHEMA = db_schema_file   
                 
    def floggerDBNameEdit2(self, mode):
        print "DB Schema File button clicked"
        if mode: 
            db_name = self.DBName.toPlainText() 
        else: 
            old_val = self.getOldValue(self.config, "FLOGGER_DB_NAME")
            self.DBName.setText(old_val)
            db_name = old_val 
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_DB_NAME", db_name) 
        self.FLOGGER_DB_NAME = db_name
                       
    def floggerFlarmnetURL2(self, mode):
        print "Flarmnet URL button clicked"
        if mode: 
            Flarmnet_URL = self.FlarmnetURL.toPlainText() 
        else: 
            old_val = self.getOldValue(self.config, "FLOGGER_FLARMNET_DB_URL")
            self.FlarmnetURL.setText(old_val)
            Flarmnet_URL = old_val 
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_FLARMNET_DB_URL", Flarmnet_URL) 
        self.FLOGGER_FLARMNET_DB_URL = Flarmnet_URL
        
                       
    def floggerOGNURL2(self, mode):
        print "OGN URL button clicked"
        if mode: 
            OGNURL = self.OGNURL.toPlainText() 
        else: 
            old_val = self.getOldValue(self.config, "FLOGGER_OGN_DB_URL")
            self.OGNURL.setText(old_val)
            OGNURL = old_val 
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_OGN_DB_URL", OGNURL) 
        self.FLOGGER_OGN_DB_URL = OGNURL
                
    def floggerSMTPServerURLEdit(self):
        print "SMTP Server URL button clicked" 
        smtp_server_URL = self.SMTPServerURL.toPlainText()  
        print "SMTP Server URL: " + smtp_server_URL
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_SMTP_SERVER_URL", smtp_server_URL)
        smtp_server_URL = self.config["FLOGGER_SMTP_SERVER_URL"]
        self.FLOGGER_SMTP_SERVER_URL = smtp_server_URL   
                      
    def floggerSMTPServerURLEdit2(self, mode):
        print "SMTP Server URL button clicked"
        if mode: 
            smtp_server_URL = self.SMTPServerURL.toPlainText()  
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_SMTP_SERVER_URL")
            self.SMTPServerURL.setText(old_val)
            smtp_server_URL = old_val
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_SMTP_SERVER_URL", smtp_server_URL)
        self.FLOGGER_SMTP_SERVER_URL = smtp_server_URL       
                      
    def floggerEmailSenderEdit2(self, mode):
        print "SMTP Sender Tx button clicked"
        if mode: 
            EmailSenderTX = self.EmailSenderTX.toPlainText()  
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_SMTP_TX")
            self.EmailSenderTX.setText(old_val)
            EmailSenderTX = old_val
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_SMTP_TX", EmailSenderTX)
        self.FLOGGER_SMTP_TX = EmailSenderTX        
                      
    def floggerEmailReceiverEdit2(self, mode):
        print "SMTP Receiver Rx button clicked"
        if mode: 
            EmailReceiverRX = self.EmailReceiverRX.toPlainText()  
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_SMTP_RX")
            self.EmailReceiverRX.setText(old_val)
            EmailReceiverRX = old_val
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_SMTP_RX", EmailReceiverRX)
        self.FLOGGER_SMTP_RX = EmailReceiverRX 
                             
    def floggerSMTPServerPortEdit2(self, mode):
        print "SMTP Server Port button clicked"
        if mode :
            smtp_server_port = self.SMTPServerPort.toPlainText()  
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_SMTP_SERVER_PORT")
            self.SMTPServerPort.setText(old_val)
            smtp_server_port = old_val
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_SMTP_SERVER_PORT", smtp_server_port)
        self.FLOGGER_SMTP_SERVER_PORT = int(smtp_server_port) 
        
    def floggerMinFlightDeltaTimeEdit2(self, mode):     
        print "Minimum Flight Difference Time button clicked"
        if mode :
            MinFlightDeltaTime = self.MinFlightDeltaTime.toPlainText()  
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_DUPLICATE_FLIGHT_DELTA_T")
            self.MinFlightDeltaTime.setText(old_val)
            MinFlightDeltaTime = old_val
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_DUPLICATE_FLIGHT_DELTA_T", MinFlightDeltaTime)
        self.FLOGGER_DUPLICATE_FLIGHT_DELTA_T = MinFlightDeltaTime
        
    def floggerFlightLogFolderEdit2(self, mode):         
        print "Flight Log Folder button clicked"
        if mode :
            FlightLogFolder = self.FlightLogFolder.toPlainText()  
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_FLIGHTS_LOG")
            self.FlightLogFolder.setText(old_val)
            FlightLogFolder = old_val
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_FLIGHTS_LOG", FlightLogFolder)
        self.FLOGGER_FLIGHTS_LOG = FlightLogFolder
        
    
                
    def floggerLandoutMsgModeEdit2(self, mode):         
        print "Landout Msg Mode button clicked"
        if mode :
            LandoutMsgMode = self.LandoutMsgMode.toPlainText()  
        else:
            old_val = self.getOldValue(self.config, "FLOGGER_LANDOUT_MODE")
            self.LandoutMsgMode.setText(old_val)
            LandoutMsgMode = old_val
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_LANDOUT_MODE", LandoutMsgMode)
        self.FLOGGER_LANDOUT_MODE = LandoutMsgMode
        
    def floggerAPRSBasesListEdit(self):
        print "APRS Bases list clicked"
#        sel_items = listWidget.selectedItems()
        sel_items = self.APRSBasesListWidget.selectedItems()
        for item in sel_items:
            new_val = item.text()
            print new_val
            item.editItem()
#            item.setText(item.text()+"More Text")
     
    def floggerAPRSBaseEdit2(self, mode):  
        print "APRS Base station list called" 
        if mode:
            APRSBaseList = []
            APRSBaseList.append(self.APRSBase1Edit.toPlainText())
            APRSBaseList.append(self.APRSBase2Edit.toPlainText())
            APRSBaseList.append(self.APRSBase3Edit.toPlainText())
            APRSBaseList.append(self.APRSBase4Edit.toPlainText())
            APRSBaseList.append(self.APRSBase5Edit.toPlainText())
            APRSBaseList.append(self.APRSBase6Edit.toPlainText())
            print "APRSBaseList: ", APRSBaseList
        else: 
            old_val = self.getOldValue(self.config, "FLOGGER_APRS_BASES")
            self.APRSBase1Edit.setText(old_val[0])
            self.APRSBase2Edit.setText(old_val[1])
            self.APRSBase3Edit.setText(old_val[2])
            self.APRSBase4Edit.setText(old_val[3])
            self.APRSBase5Edit.setText(old_val[4])
            self.APRSBase6Edit.setText(old_val[5])
            APRSBaseList = old_val
        APRSBaseList = [str(APRSBaseList[0]), 
                        str(APRSBaseList[1]), 
                        str(APRSBaseList[2]), 
                        str(APRSBaseList[3]), 
                        str(APRSBaseList[4]), 
                        str(APRSBaseList[5])]
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_APRS_BASES", APRSBaseList)
        self.FLOGGER_APRS_BASES = APRSBaseList 
        print "FLOGGER_APRS_BASES: ", self.FLOGGER_APRS_BASES

    def floggerAdd2FleetOkButton(self):
        print "floggerAdd2FleetOkButton called"
        if self.Add2FleetRegEdit.toPlainText() == "":
            return
        rowPosition = self.FleetListTable.rowCount()          
#            print "rowPosition: ", rowPosition, " Registration: ", registration, " Code: ", settings.FLOGGER_FLEET_LIST[registration]
        self.FleetListTable.insertRow(rowPosition)
#        self.FleetListTable.setItem(rowPosition , 0, QtGui.QTableWidgetItem(self.Add2FleetRegEdit))
        self.FleetListTable.setItem(rowPosition , 0, QtGui.QTableWidgetItem(self.Add2FleetRegEdit.toPlainText()))
        self.FleetListTable.setItem(rowPosition , 1, QtGui.QTableWidgetItem(self.Add2FleetCodeEdit.toPlainText())) 
        # Add in the new registration to the dictionary 
        old_fleet_list = self.getOldValue(self.config, "FLOGGER_FLEET_LIST") 
        old_fleet_list[str(self.Add2FleetRegEdit.toPlainText())] = str(self.Add2FleetCodeEdit.toPlainText())
        # Output the updated FleetList to the config file
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_FLEET_LIST", old_fleet_list)
        settings.FLOGGER_FLEET_LIST = old_fleet_list
        print "FLOGGER_FLEET_LIST: ", settings.FLOGGER_FLEET_LIST
        # Set fields on form to balnk
        self.Add2FleetRegEdit.setText("")
        self.Add2FleetCodeEdit.setText("")   
        
    def floggerAdd2FleetCancelButton(self): 
        print "floggerAdd2FleetCancelButton called"
        self.Add2FleetRegEdit.setText("")
        self.Add2FleetCodeEdit.setText("")  
        
    def floggerDelFromFleetOkButton(self):
        print "floggerDelFromFleetOkButton"
        if self.DelFromFleetEdit.toPlainText() == "":
            return
        fleet_list = self.getOldValue(self.config, "FLOGGER_FLEET_LIST") 
        reg = self.DelFromFleetEdit.toPlainText()
        del fleet_list[str(reg)]
#        print "fleet_list: ", fleet_list
        self.editConfigField("flogger_settings_file.txt", "FLOGGER_FLEET_LIST", fleet_list)
        settings.FLOGGER_FLEET_LIST = fleet_list
        self.DelFromFleetEdit.setText("")
        
        old_val = self.getOldValue(self.config, "FLOGGER_FLEET_LIST")
        print "FLOGGER_FLEET_LIST now: ", self.FLOGGER_FLEET_LIST 
        for key in old_val.keys():
            # Convert string form of value to int
            old_val[key] = int(old_val[key])
#            print "Key: ", key, " = ", int(old_val[key])
        print "FLOGGER_FLEET_LIST: ", settings.FLOGGER_FLEET_LIST
        
        self.FleetListTable.clearContents()
        self.FleetListTable.setRowCount(0)
        rowPosition = self.FleetListTable.rowCount()
#        rowPosition = 0
        for registration in settings.FLOGGER_FLEET_LIST:
            print "rowPosition: ", rowPosition, " Registration: ", registration, " Code: ", settings.FLOGGER_FLEET_LIST[registration]
            self.FleetListTable.insertRow(rowPosition)   
            self.FleetListTable.setItem(rowPosition , 0, QtGui.QTableWidgetItem(registration))
            self.FleetListTable.setItem(rowPosition , 1, QtGui.QTableWidgetItem(str(settings.FLOGGER_FLEET_LIST[registration])))
            rowPosition = rowPosition + 1 # interesting rowPosition =+ 1 gives wrong result!!
    
    def floggerOkpushButton(self):
        print "About Ok button clicked"
        self.close()
        
    def floggerFlightLog(self):
        
        def setColourtoRow(table, rowIndex, colour):
            for j in range(table.columnCount()):
                table.item(rowIndex, j).setBackground(colour)
                
        print "Flight Log calendar clicked"
        date_conv = time.strptime(str(self.FlightLogcalendar.selectedDate().toString()),"%a %b %d %Y")
#        print time.strftime("%d/%m/%Y",date_conv)
        date = time.strftime("%y/%m/%d",date_conv)
        print date
        # Get flights for date
        try:
#            db = sqlite3.connect(os.path.join(path,settings.FLOGGER_DB_NAME)) 
#            print "DB name: ", os.path.join(path,settings.FLOGGER_DB_NAME)
            flogger_db_path = path_join_dd(os.path.abspath(__file__), ["db", "flogger.sql3.2"])
            print "DB name(new): ", flogger_db_path
            db = sqlite3.connect(flogger_db_path) 
            cursor = db.cursor()
        except:
            print "Failed to connect to db"
        try:
            cursor.execute("SELECT flight_no, sdate, stime, etime, duration, src_callsign, max_altitude, registration, track_file_name, tug_registration, tug_altitude, tug_model  FROM flights WHERE sdate=? ORDER BY stime DESC", (date,))
        except:
            print "Select failed"
        rows = cursor.fetchall()
        row_count = cursor.rowcount
        print "row_count: ", row_count
        header = self.FlightLogTable.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.Stretch)
        col_nos = 0
        while col_nos < 9:
            header.setResizeMode(col_nos, QtGui.QHeaderView.ResizeToContents)
            col_nos = col_nos + 1
        self.FlightLogTable.clearContents()
        self.FlightLogTable.setRowCount(0)
        rowPosition = self.FlightLogTable.rowCount()
        self.FlightLogTable.setColumnHidden(10, True)
#        row_count = 1
        for row in rows:  
#            print "Row: ", row_count 
            try:
                if settings.FLOGGER_FLEET_LIST[row[7]] > 100 and \
                    settings.FLOGGER_FLEET_LIST[row[7]] <= 200 and \
                    settings.FLOGGER_INCLUDE_TUG_FLIGHTS <> "Y":
                    print "Tug only flight so ignore tug: ", row[7]
                    continue
            except KeyError:
                print "Glider not in Fleet hence not a tug: ", row[7]                        
            self.FlightLogTable.insertRow(rowPosition)   
            if row[9] is None:
                val = "----"
            else:
                val = row[9]
            self.FlightLogTable.setItem(rowPosition , 0, QtGui.QTableWidgetItem(val))           # Tug Reg
            if row[11] is None:
                val = "----"
            else:
                val = row[11]
            self.FlightLogTable.setItem(rowPosition , 1, QtGui.QTableWidgetItem(val))           # Tug Type
            self.FlightLogTable.setItem(rowPosition , 2, QtGui.QTableWidgetItem(row[7]))        # (Moto) Glider     
            self.FlightLogTable.setItem(rowPosition , 3, QtGui.QTableWidgetItem(row[7][3:]))    # CN
            cursor.execute("SELECT aircraft_model FROM flarm_db WHERE registration = ?", (row[7],))
            plane_type = cursor.fetchone()
            if plane_type[0] == None:
                print "Aircraft_model not found, try Type for Registration : ", row[7]
                cursor.execute("SELECT type FROM flarm_db WHERE registration = ?", (row[7],))   
                plane_type = cursor.fetchone()
            print "Plane Type/model is: ", plane_type[0]
            self.FlightLogTable.setItem(rowPosition , 4, QtGui.QTableWidgetItem(plane_type[0])) # Plane Type/Model 
            self.FlightLogTable.setItem(rowPosition , 5, QtGui.QTableWidgetItem(row[2]))        # Glider Takeoff TIme
            self.FlightLogTable.setItem(rowPosition , 6, QtGui.QTableWidgetItem(row[3]))        # Glider Landing Time
            self.FlightLogTable.setItem(rowPosition , 7, QtGui.QTableWidgetItem(row[4]))        # Glider Flight Time
            if row[10] is None:
                val = "----"
            else:
                val = row[10]
            self.FlightLogTable.setItem(rowPosition , 8, QtGui.QTableWidgetItem(val))            # Tug Max ALt (QFE)
            self.FlightLogTable.setItem(rowPosition , 9, QtGui.QTableWidgetItem(row[6]))
            self.FlightLogTable.setItem(rowPosition , 10, QtGui.QTableWidgetItem(row[8]))

            if row_count % 2 == 0:
                colour = QtGui.QColor(204,255,204)      # Light green 
            else:
                colour = QtGui.QColor(128,255,128)      # Darker green
            setColourtoRow(self.FlightLogTable, rowPosition, colour)     
            row_count = row_count + 1

    def floggerFlightLogDoubleClicked(self):
        print "Double Clicked called"
        self.FlightLogTable.setColumnHidden(10, False)
        index = self.FlightLogTable.selectedIndexes()
        
        print 'selected item index found at %s with data: %s' % (index[10].row(), index[10].data().toString())
        track_file = index[10].data().toString()
        self.FlightLogTable.setColumnHidden(10, True)    
        gpx_file = open(track_file, 'r')
        gpx = gpxpy.parse(gpx_file)       
        lat = []
        lon = []   
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    lat.append(point.latitude)
                    lon.append(point.longitude)
        #fig = plt.figure(facecolor = '0.05')
        fig = plt.figure(facecolor = 'w')
        ax = plt.Axes(fig, [0., 0., 1., 1.], )
        ax.set_aspect('equal')
        ax.set_axis_off()
        fig.add_axes(ax)
        plt.plot(lon, lat, color = 'black', lw = 1.0, alpha = 0.8)
        mplleaflet.show()
        
        
        
#
# Utility functions
#          
    def editConfigField (self, file_name, field_name, new_value):
        print "editConfig called"
        self.config[field_name] = new_value
        self.config.write()
#        setattr(self, field_name, new_value) #equivalent to: self.'field_name' = new_value
        if type(new_value) is int: 
            int(new_value)
#        setattr(self, field_name, new_value) #equivalent to: self.'field_name' = new_value
        setattr(settings, field_name, new_value) #equivalent to: settings.'field_name' = new_value
            
    def setOldValue(self, config_field_name): 
#        val = self.config[config_field_name]
        val = settings.config[config_field_name]
        setattr(self, config_field_name, val) #equivalent to: self.varname= 'something'
#        settings.config_field_name = val
        return self.config[config_field_name]
    
    def getOldValue(self, config, config_field_name): 
        val = config[config_field_name]
        setattr(self, config_field_name, val)
        return config[config_field_name]
    
    def AboutButton(self):
        print "About menu clicked"
        window = AboutWindow(self)
        window.show()
          
    def HelpButton(self):
        print "Help menu clicked"
        window = HelpWindow(self)
        window.show()
#
# Actions End
#            
    


class Form(QDialog):
    """ Just a simple dialog with a couple of widgets
    """
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.browser = QTextBrowser()
        self.setWindowTitle('Just a dialog')
        self.lineedit = QLineEdit("Write something and press Enter")
        self.lineedit.selectAll()
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.lineedit)
        self.setLayout(layout)
        self.lineedit.setFocus()
        self.connect(self.lineedit, SIGNAL("returnPressed()"), self.update_ui)

    def update_ui(self):
        self.browser.append(self.lineedit.text())

#
# Start of Flogger execution
#
if __name__ == "__main__":
	main()

    
