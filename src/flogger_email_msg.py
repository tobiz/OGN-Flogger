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

def email_msg(sender, receiver, msg, date, settings):
#    print "Send take off msg"
    if settings.FLOGGER_TAKEOFF_EMAIL != "y" and settings.FLOGGER_TAKEOFF_EMAIL != "Y":
        # Don't send take off email msg
        return
#    body = "Msg from %s. %s taken off @ %s" % (settings.APRS_USER, msg, date)  
    body = "%s. %s taken off @ %s" % (settings.APRS_USER, msg, date)  
    print body
    msg = MIMEMultipart() 
    msg.attach(MIMEText(body, 'plain'))
 
    fromaddr = sender
    toaddr = receiver  
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] =  body 
    
    server = smtplib.SMTP(settings.FLOGGER_SMTP_SERVER_URL, settings.FLOGGER_SMTP_SERVER_PORT)
    text = msg.as_string()
#    print "Msg string is: ", text
    try:
        server.sendmail(fromaddr, toaddr, text)
    except Exception as e:
        print "Send email_msg failed, reason: ", e
    server.quit()
    return
       