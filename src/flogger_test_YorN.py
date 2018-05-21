#
#-----------------------------------------------------------------
# Function to test whether supplied parameter is "Y" or "y" or "N" or "n"
# 
# Returns True for Y|y and False for N|n
# 
# 
#-----------------------------------------------------------------
#

import flogger_settings
import string
#import datetime
#import time
#import sqlite3
#import pytz
#from datetime import timedelta
#import sys
#from flarm_db import flarmdb
#from pysqlite2 import dbapi2 as sqlite
#from open_db import opendb 

def test_YorN(value):
    #
    # Tests value for Y|y of N|n
    # Returns: True for Y|y and False for N|n
    #
    if value == "Y" or value == "y":
    	return True 
    if value == "N" or value == "n":
    	return False
    
    
    