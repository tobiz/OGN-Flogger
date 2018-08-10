import smtplib
import base64
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from __builtin__ import file
import os
import datetime

def email_log2(sender, receiver, filepath, date, settings):
#    print "email_log2 with sender=%s, receiver=%s, filepath=%s" % (sender, receiver, filepath)
    FLIGHT_LOG_FILE = "flight_log.csv"
#    filepath = path + file
    fpr = open(filepath, "r")
    fpw = open(FLIGHT_LOG_FILE, "w+")                # Read and write
    data_lines = fpr.read()
    line_list = data_lines.split("\n")
#    print "Line_list is: ", line_list
    for aline in line_list:
        if aline == "":
            print "BREAK end of flights.csv"
            break
#        print "Aline is: ", aline
        pl = aline.split(",")  
        spl = pl[0:8]  
#        print "Pl is: ", pl
        npl = "%s,%s,%s,%s,%s,%s,%s,%s\n" % (str(pl[0]), str(pl[1]), str(pl[2]), str(pl[3]), str(pl[4]), str(pl[5]), str(pl[6]), str(pl[7]))
#        print "npl is: ", npl
        fpw.write(npl)
#    return
    fpw.close()
    fromaddr = sender
    toaddr = receiver  
    print "From: " + fromaddr + " To: " + toaddr
    msg = MIMEMultipart() 
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] =  "Flight log for today: %s from %s" % (date, settings.APRS_USER)  
    if os.path.getsize(filepath) == 0:
        print "No file to attach"
        body = "No flights for today: %s" % date
        msg.attach(MIMEText(body, 'plain')) 
    else:  
        # There is a flight log for today so attach it 
        print "Attach file"
        body = "Flight log for : %s" % date
        msg.attach(MIMEText(body, 'plain')) 
        attachment = open(FLIGHT_LOG_FILE, "r+")  
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % FLIGHT_LOG_FILE)  
        msg.attach(part)
    
#    print "SMTP URL: " + str(settings.FLOGGER_SMTP_SERVER_URL) + " SMTP Port: " + str(settings.FLOGGER_SMTP_SERVER_PORT)
    try:
        server = smtplib.SMTP(str(settings.FLOGGER_SMTP_SERVER_URL), str(settings.FLOGGER_SMTP_SERVER_PORT))
#        server = smtplib.SMTP(settings.FLOGGER_SMTP_SERVER_URL, int(settings.FLOGGER_SMTP_SERVER_PORT))
#        print "SMTP Server connection ok"
    except:
        print "SMTP Server connection failed"
    text = msg.as_string()
    print "Msg string is: ", text
    try:
        server.sendmail(fromaddr, toaddr, text)
#        print "Sendmail ok"
    except:
        print "Sendmail failed"
    server.quit()
    fpw.close()
    try:
        os.remove(FLIGHT_LOG_FILE)
    except Exception, e:
        print "Remove FLIGHT_LOG_FILE failed, reason: ", e
    return
       



