from pysqlite2 import dbapi2 
import sqlite3
#import flogger_settings

def opendb (schema_file, cursor):
    # Open a connection to the database
    # Build the database from the supplied schema
    print "opendb"
    try:
        db = sqlite3.connect("flogger.db")
    except Exception as e:
        # Failed to open flogger.db, error
        print "Failed to open flogger.db, error"
        return False
    
    # Create a cursor to work with
    cur = db.cursor()
    cursor[0] = cur
    
    # --DROP tables if they exist in the database 
    floggerSchema = open(schema_file)
#    print "OGN-Flight-Logger-Schema.sql open ok"
    print "opendb: ", schema_file, " open ok"
    schemaStr = ""
    for line in floggerSchema.readlines():
#        print "Line is: ", line
        schemaStr += " %s" % line
#    print "schemaStr is: ", schemaStr
    try:
        cur.executescript(schemaStr)
    except Exception as e:
        # Failed to create flogger.db from schema, error
        print "Failed to create flogger.db from schema, error"
        return False
    floggerSchema.close()
    db.commit()
    db.close()
    print "opendb: Flogger Databases built"
    return True

# cur = [0]    # cur is mutable
# r = opendb("flogger_schema-0.0.1.sql", cur)  
# r = opendb(settings.FLOGGER_DB_SCHEMA, cur)
# print "End: ", r, ". cur is: ", cur
