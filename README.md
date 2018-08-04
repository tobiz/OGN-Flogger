# OGN-Flight-Logger_V4
DEVELOPMENT OF OGN-Flight-Logger IS NOW CONTINUING AS: OGN-Flight-Logger_V4

Python APRS/OGN program to log flight times, durations and maximum heights achieved

V4 is functionally the same as V3 but is under development for:

- Packaging for installation using PyPi
- Removal of libfap for parsing APRS packets (libfap not available on Windows)
- Restructing code to be more 'compliant', eg separation of code and data into separate directories
- Various changes with the intention of being installable on Microsoft Windows

Installation

To install Flogger you will need to have installed:

'geocoder>=1.4.0',
'parse>=1.8.0',
'configobj>=4.7.2',
'geopy>=1.11.0',
'aerofiles>=0.3',
'aprslib>=0.6.46',
'gpxpy>=1.1.2',
'setuptools>=3.3',
'pytz>=2012c',
'requests>=2.13.0',
'mplleaflet>=0.0.5',
'LatLon>=1.0.2',
'PyQt4>=4.11.4',
'pyephem>=3.7.6.0',
'protobuf>=3.5.2.post1',
'adhocracy_pysqlite>=2.6.3',
'pysqlite3>=0.1.0',
'matplotlib'

The tricky ones to install are: PyQt4 and pysqlite3.
To install PyQT4 on Linux based systems see: http://problemssol.blogspot.com/2010/12/compile-and-install-pyqt4-for-python27.html.

Running

Once installed to run call flogger_gui.py.

To run Flogger once installed run "flogger_gui.py". This starts the system displaying a splash screen whilst building the gui, once this has been done then control is via the gui.

You will need to set up your own values for the "APRS Setup" tab fields, in particular the "APRS Usernams" and "APRS Passcode" fields. "APRS Server Host" and "APRS Server Port" can be left. The "APRSBase Station" fields should be set to your required values, there need only be 1 but more gives a better result.

"APRS Usernams" and "APRS Passcode" can be created on http://http://www.george-smart.co.uk/wiki/APRS_Callpass
If a valid username and passcode are not suppled it will exit immediately.

After that go through each tab providing your values. Airfield Lat/Lon do not have to be supplied if "Airfield Details" is supplied as a valid airfield name, if it is, the Lat/Lon and QNH are taken from a database.

I would recommend the "Advanced" field is not changed.

Testing

The results produced by Flogger have been compared against those from Ktrax and are  pretty comparable.  Flogger has be set up for my home site and run for several days, the results being checked against Ktrax.  Flogger has also been set up for another site and the results compared against those from Ktrax.


History

This python program creates an SQlite db of flights from a given location and aircraft list 
(the later two parameters are to be be developed into a more generalised format).

At the moment this is very much 'in development'
(This is a development of V2 which got screwed up when I tried to to create a PyPi package)

Note, the following is now handled by the gui.
 
To run flogger first set up the parameters in settings.py then call 'flogger.py'.  Flogger.py will
run continuously (perhaps it should be a 'service'?) logging flights during day, ie between sunrise
and sunset. After sunset it processes the days log to determine which log entries constitute actual flights
and those which are ground movements etc. Once all the flights have been generated into the 'flights' table and
the days flights dumped as a .csv file, flogger determines when the next sunrise time and sleeps until then, ie waits.

If installing on an arm based system this can be achieved by:

- sudo apt-get install python-tz sqlite3
- wget http://www.pakettiradio.net/downloads/libfap/1.5/libfap6_1.5_armhf.deb
- sudo dpkg -i libfap*.deb

- sudo apt-get install pythonX-dev where X is version of python being used
- sudo apt-get install python-pip
- sudo pip install pyephem 
- sudo pip install geopy
- sudo pip install geocoder
- sudo pip install aerofiles

I'm currently developing and testing on
- a Raspberry Pi P2 Model B under Rasparian (Debian Linux 7.8) and 
- a desktop running Kubuntu 14.04 

Flogger has been updated to optionally record flight tracks and output these as .gpx files.
This enhancement is still in development.  This feature is controlled in the settings.py file

Flogger will now optionally take inputs from upto 4 base stations.  It also has an option to delete flight and track .csv files after
they are "n" days old.  Track points are sorted and output to .csv files based on the logged time from the Flarm unit itself (assumes Flarms
use GPS time in each trackpoint).  This is to over come a potential issue using multiple base stations when the track points might not be received in the same
time order as they were sent from the flarm units.

This now in the latter stages of development, it still logs a lot of test output but his will eventually be controlled by an option
from the cmd line and/or configuration file

9th March 2016 
Added an option to output IGC format track files. This requires aerofiles.py to be installed (see above).  Several optional fields in the 
header are set to "Not recorded" as these can not be known by OGN Flogger, however if this data was input prior to launch it could, but
that's another development..... Note the files output are not 'certified'.

Added an option to specify number of hours before sunset that processing the flight logs should commence.

Added an option to send the daily flight log to a specified email address in .csv format.
The cmd line form is:
flogger.py username passcode mode [-s|--smtp email address of smtp server] [-t|--tx email address of sender] [-r|--rx email address of receiver]

If -s|--smtp is provided then -t|--tx and -r|--rx must be provided

Included option to send email if flight lands outside the take off airfield.  This initial version just uses a circular boundary of a specifiable radius.  Code is included to 
send an SMS msg but has not been tested.

Update History

20160914 - Added option to determine which tug used for a launch, if any, plus release height.

20170213 - Next phase of the development is to control running and configuring the code from a gui. At the moment
			this is highly experimental. This uses PyQt as the api and Qt Designer for building the graphical interface. 
			
20170215 - User defined configuration data is held in data formats defined by ConfigObj 4, 
			see http://www.voidspace.org.uk/python/configobj.html
			
20170226 - Please note at this stage the user interface is purely on the basis of understanding how the code works and is not intended to be the final design.

20170304 - Flogger now runs as a separate process to the gui (I think?) Still some issues with access to some variables from settings data which results in an exception and crash (catch the exception in try statement when calling the process? Maybe).

20170310 - The intention is to remove separate Edit buttons for each field and replace by a single one which when clicked will update all changed fields. There will also be a Cancel button to 'undo' any changed fields (for now this will be limited to a single undo level, muliple undo levels is for later(!)); so far this feature has been shown to work on 2 fields. In addition the Python Packaging 'setup' files have been added for uploading OGN-Flogger to PyPi, and something(?) has been added to the PyPi index (but not convinced it installs correctly at the moment).

20170312 - First commit of V3

20170313 - Add explanation of differences between V2 and V3.

20170323 - First complete test version of gui controlled application

20170323 - Added files for PyPi packaging compatibility.

20170324 - OGN-Flogger pypi package installed on PyPi will not install from there. The reason is not OGN-Flogger but PyQt4.  Despite PyQt4 being available from PyPi it cannot be installed using pip (and hence not as a dependency when installing OGN-Flogger).  To install PyQt4 (which together with QT4 Designer, are a great product), go to https://www.riverbankcomputing.com/software/pyqt/download and follow the instructions there.

20170424 - New tab added to display flight log details

20170425 - To install from PyPi you need to first install python-sip and python-pyqt4. This can be done by: sudo apt-get install python-sip python-qt4 or similar. Once these have been installed then OGN-Flogger can be installed from PyPi by: pip install OGN-Flogger.

20170426 - OGN-Flogger is now available on PyPi. Please note the sip/pyqt4 issue above when trying to install.

20170505 - Added facility to display flight tracks on OpenStreetMap map by double clicking on selected flight in flight log table.

20180114 - To run the gui version call "flogger_gui.py".

20180521 - V4 version started (I'm no git expert!)

20180729 - Changes to gui to determine Lat/Lon if airfield details supplied. Start of updates to README.


