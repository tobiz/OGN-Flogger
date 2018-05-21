#
# This function determines if a flight has landed outside the airfield.
# The perimiter of the airfield is taken as circle based on the designated centre point
# of a specified radius. This is not the most accurate but will do to start with.
# If a flight lands outside the airfield then an SMS message with there landing coordinates
# is sent to a specified number.

import smtplib
import base64
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from __builtin__ import file
import  flogger_settings
import os
import datetime
from geopy.distance import vincenty
from flogger_get_coords import get_coords
#from google.directions import GoogleDirections
from LatLon import  * 

def landout_check(flight_reg, flight_no, af_centre, radius, landing_coords, mode, settings):
    #
    # This function determines if a flight has landed within the vicinity of the airfield take off point.
    # If not it sends an email to the designated address specifying the landing coordinates, these
    # can then be used by the recovery team to locate the aircraft using appropriate mapping technology.
    # The algorithm used is that of a circle of defined radius centred on the originating airfield.
    # The function is intended to send the msg either by email or SMS but at the moment only email
    # is supported.  The SMS code is included, has not been tested and requires an account to be created
    # and of course each SMS msg would be charged to that account.  The provenance of the SMS code is
    # included if this helps with subsequent development.
    #
    # Returns: True - landed out.  False - landed inside airfield limits
    #
    print "landout_check called. Registration: ", flight_reg, " Start coords: ", af_centre, " End coords: ", landing_coords
    print "settings.FLOGGER_SMTP_SERVER_URL: ", settings.FLOGGER_SMTP_SERVER_URL, " settings.FLOGGER_SMTP_SERVER_PORT: ", settings.FLOGGER_SMTP_SERVER_PORT   
    landing_dist = vincenty(af_centre, landing_coords).meters
    print "Landing distance is: %d metres from airfield centre" % landing_dist
    if landing_dist <= radius:
        landing_status = "landed"
        result = False
        print "Landed in airfield"
    else:
        landing_status = "landed out"
        result = True
        print "Flight landed out, send msg. Registration: ", flight_reg, " Flight No: ", flight_no
        
    # Is an email or SMS of landing status requested?
    if settings.FLOGGER_LANDING_EMAIL <> "Y" and settings.FLOGGER_LANDING_EMAIL <> "y":
        # No email or SMS of landing status required, return landing status
        return result
    #
    # Email or SMS of landed status to be sent
    #   
    landing_point = LatLon(landing_coords[0], landing_coords[1])   # Decimal degrees to object
    landing_coords = landing_point.to_string('d% %m% %S% %H')   # Coordinates to degrees minutes seconds 
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")    # Date and time of event
    
    if mode == "SMS":
        #-----------------------------------
        # Send SMS Text Message using Python
        #
        # Author : Matt Hawkins
        # Site   : http://www.raspberrypi-spy.co.uk/
        # Date   : 01/04/2016
        #
        # Requires account with TxtLocal
        # http://www.txtlocal.co.uk/?tlrx=114032
        #
        #-----------------------------------
         
        # Import required libraries
        import urllib      # URL functions
        import urllib2     # URL functions
         
        # Set YOUR TextLocal username
        username = 'joebloggs@example.com'
         
        # Set YOUR unique API hash
        # It is available from the docs page
        # https://control.txtlocal.co.uk/docs/
        hash = '1234567890abcdefghijklmnopqrstuvwxyz1234'
         
        # Set a sender name.
        # Sender name must alphanumeric and 
        # between 3 and 11 characters in length.
        sender = 'RPiSpy'
        sender = settings.FLOGGER_YGC_ADMIN
         
        # Set flag to 1 to simulate sending
        # This saves your credits while you are
        # testing your code.
        # To send real message set this flag to 0
        test_flag = 1
         
        # Set the phone number you wish to send
        # message to.
        # The first 2 digits are the country code.
        # 44 is the country code for the UK
        # Multiple numbers can be specified if required
        # e.g. numbers = ('447xxx123456','447xxx654321')
        numbers = ('447xxx123456')
         
        # Define your message
        message = 'Test message sent from my Raspberry Pi'
         
        #-----------------------------------------
        # No need to edit anything below this line
        #-----------------------------------------
         
        values = {'test'    : test_flag,
                  'uname'   : username,
                  'hash'    : hash,
                  'message' : message,
                  'from'    : sender,
                  'selectednums' : numbers }
         
        url = 'http://www.txtlocal.com/sendsmspost.php'
         
        postdata = urllib.urlencode(values)
        req = urllib2.Request(url, postdata)
         
        print 'Attempt to send SMS ...'
         
        try:
          response = urllib2.urlopen(req)
          response_url = response.geturl()
          if response_url==url:
            print 'SMS sent!'
            return result
        except urllib2.URLError, e:
          print 'Send failed!'
          print e.reason
          return result
    #
    # Send landing status as email
    #
    if mode == "email":
        print "Send %s email" % landing_status
        fromaddr = settings.FLOGGER_SMTP_TX
        toaddr = settings.FLOGGER_SMTP_RX
        msg = MIMEMultipart() 
        msg['From'] = fromaddr
        msg['To'] = toaddr
        txt = "%s: %s %s at: %s. Time: %s" % (settings.APRS_USER, flight_reg, landing_status, landing_coords, now)

        msg['Subject'] =  txt 
        print "Email %s coordinates: %s" % (landing_status, txt)
        body = txt + " Flight No: " + str(flight_no)
        msg.attach(MIMEText(body, 'plain')) 
        print "settings.FLOGGER_SMTP_SERVER_URL: ", settings.FLOGGER_SMTP_SERVER_URL, " settings.FLOGGER_SMTP_SERVER_PORT: ", settings.FLOGGER_SMTP_SERVER_PORT   
        server = smtplib.SMTP(settings.FLOGGER_SMTP_SERVER_URL, settings.FLOGGER_SMTP_SERVER_PORT)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
    return result

#
# Test call
#

#af_centre = get_coords(settings.FLOGGER_AIRFIELD_DETAILS)
#print "Airfield coords: ", af_centre
#radius = settings.FLOGGER_AIRFIELD_LIMIT
#radius = 44000
#mode = settings.FLOGGER_LANDOUT_MODE
#landing_coords = get_coords("Pocklington")
#print "Pocklington coords: ", landing_coords
#settings.FLOGGER_SMTP_SERVER_URL = "smtp.metronet.co.uk"
#settings.FLOGGER_SMTP_SERVER_PORT = 25
#settings.FLOGGER_SMTP_TX = "pjrobinson@metronet.co.uk"
#settings.FLOGGER_SMTP_RX = "pjrobinson@metronet.co.uk"
#landout_check("GB_JVC", af_centre, radius, landing_coords, mode)
        