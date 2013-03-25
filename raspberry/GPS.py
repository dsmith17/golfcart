import io
import time
import serial #Has to be installed from pyserial.sourceforge.net/
from log import *

GPSConnected = False
GPS_Port = ''

# Serial port used to communicate with GPS
def open(port) :
    global GPS_Port
    global GPSConnected
    try :
        GPS_Port = serial.Serial(port, 4800, timeout=0)
        GPSConnected = True
        writeLog(LOG_DETAILS, 'Connected to GPS: ' + str(port))
    except Exception as err :
        writeLog(LOG_ERROR, 'Unable to connect to GPS: ' + str(port))

GPS_lat = 0.0
GPS_long = 0.0
GPS_dir = 0.0
GPS_speed = 0.0
GPS_time = 0.0
GPS_Buffer = ' '

def GPS_valid_msg(msg) :
  try:
    valid = True
    if msg[0] != '$' :
        return False

    checksum = 0
    p = 1
    c = ord(msg[p])
    while chr(c) != '*' and p < len(msg) :
        checksum = checksum ^ c
        p = p + 1
        c = ord(msg[p])
    if msg[p] != '*' :
        return False
    
    nmeaCheck = int(msg[p+1:p+3], 16)

    return nmeaCheck == checksum
  except Exception as err :
      writeLog(LOG_ERROR, 'Exception in GPS_valid_msg: ' + str(err))
      print 'invalid GPS: ', msg, len(msg), p
      return False

def GPS_set_time(val) :
    global GPS_time
    new_time = float(val)
    if new_time != GPS_time :
        GPS_time = new_time
        writeLog(LOG_GPS_TIME, 'GPS time: ' + str(GPS_time))

def GPS_set_lat_long(lat, lat_hemi, longt, longt_hemi) :
    global GPS_lat
    global GPS_long
    
    if len(lat) == 0 or len(longt) == 0 :
        return

    new_lat = float(lat[0:2]) + float(lat[2:])/60
    if lat_hemi == 'S' :
        new_lat = -new_lat
        
    new_long = float(longt[0:3]) + float(longt[3:])/60
    if longt_hemi == 'E' :
        new_long = -new_long
        
    if new_lat != GPS_lat or new_long != GPS_long :
        writeLog(LOG_GPS_POS, 'GPS pos: ' + str(new_lat) + ' ' + str(new_long))
    GPS_lat = new_lat
    GPS_long = new_long
    
def GPS_set_speed(val) :
    global GPS_speed
    if len(val) != 0 :
        new_speed = float(val)

        if new_speed != GPS_speed :
            writeLog(LOG_GPS_SPEED, 'GPS speed: ' + str(new_speed))
            GPS_speed = new_speed
def GPS_set_dir(val) :
    global GPS_dir
    if len(val) != 0 :
        new_dir = float(val)
        if new_dir != GPS_dir :
            GPS_dir = new_dir
            writeLog(LOG_GPS_DIR, 'GPS dir: ' + str(GPS_dir))

def GPGGA(fields):
    GPS_set_time(fields[1])
    GPS_set_lat_long(fields[2],fields[3],fields[4], fields[5])
def GPGLL(fields):
    GPS_set_time(fields[5])
    GPS_set_lat_long(fields[1],fields[2],fields[3], fields[4])   
def GPGSA(fields):
    # GPS satelite data and whether locked or not
    pass
def GPRMC(fields):
    GPS_set_time(fields[1])
    GPS_set_lat_long(fields[3],fields[4],fields[5], fields[6])
    GPS_set_speed(fields[7])
    GPS_set_dir(fields[8])
def GPGSV(fields) :
    # GPS satelite data and quality
    pass
def GPVTG(fields):
    GPS_set_speed(fields[3])
    GPS_set_dir(fields[1])

GPS_func = {'$GPVTG': GPVTG,
            '$GPGGA': GPGGA,
            '$GPGLL': GPGLL,
            '$GPGSA': GPGSA,
            '$GPRMC': GPRMC,
            '$GPGSV': GPGSV}

def checkGPS():
    global GPS_Port
    global GPSConnected
    global GPS_Buffer

    if not GPSConnected :
        return

    count = GPS_Port.inWaiting()
    if (count > 0) :
        buff = GPS_Port.read(size=count)
        GPS_Buffer = GPS_Buffer + buff
        
    start = GPS_Buffer.find('$')
    if start == -1 :
        GPS_Buffer = ''
        return
    while start > 0 :
        end = GPS_Buffer.find('\r',start)
        if end == -1 :
            return
        
        line = GPS_Buffer[start:end]
        GPS_Buffer = GPS_Buffer[end:]

        if len(line) < 5 :
            return
        if not GPS_valid_msg(line) :
            writeLog(LOG_ERROR, 'GPS checksum error ' + line)
            return

        writeLog(LOG_GPS_RAW, line)
        fields = line.split(',')
    
        try :
            GPS_func[fields[0]](fields)
        except KeyError as err :
            writeLog(LOG_ERROR, 'unknown GPS command: '+line)

        start = GPS_Buffer.find('$')
