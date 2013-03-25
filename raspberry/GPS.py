import io
import time
import serial #Has to be installed from pyserial.sourceforge.net/
from log import *

Connected = False
_Port = ''

# Serial port used to communicate with GPS
def open(port) :
    global _Port
    global Connected
    try :
        _Port = serial.Serial(port, 4800, timeout=0)
        Connected = True
        writeLog(LOG_DETAILS, 'Connected to GPS: ' + str(port))
    except Exception as err :
        writeLog(LOG_ERROR, 'Unable to connect to GPS: ' + str(port))

Latitude = 0.0
Longitude = 0.0
Direction = 0.0
Speed = 0.0
Time = 0.0
_Buffer = ' '

def _valid_msg(msg) :
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

def _set_time(val) :
    global Time
    new_time = float(val)
    if new_time != Time :
        Time = new_time
        writeLog(LOG_GPS_TIME, 'GPS time: ' + str(Time))

def _set_lat_long(lat, lat_hemi, longt, longt_hemi) :
    global Latitude
    global Longitude
    
    if len(lat) == 0 or len(longt) == 0 :
        return

    new_lat = float(lat[0:2]) + float(lat[2:])/60
    if lat_hemi == 'S' :
        new_lat = -new_lat
        
    new_long = float(longt[0:3]) + float(longt[3:])/60
    if longt_hemi == 'E' :
        new_long = -new_long
        
    if new_lat != Latitude or new_long != Longitude :
        writeLog(LOG_GPS_POS, 'GPS pos: ' + str(new_lat) + ' ' + str(new_long))
    Latitude = new_lat
    Longitude = new_long
    
def _set_speed(val) :
    global Speed
    if len(val) != 0 :
        new_speed = float(val)

        if new_speed != Speed :
            writeLog(LOG_GPS_SPEED, 'GPS speed: ' + str(new_speed))
            Speed = new_speed
def _set_dir(val) :
    global Direction
    if len(val) != 0 :
        new_dir = float(val)
        if new_dir != Direction :
            Direction = new_dir
            writeLog(LOG_GPS_DIR, 'GPS dir: ' + str(Direction))

def _GPGGA(fields):
    _set_time(fields[1])
    _set_lat_long(fields[2],fields[3],fields[4], fields[5])
def _GPGLL(fields):
    _set_time(fields[5])
    _set_lat_long(fields[1],fields[2],fields[3], fields[4])   
def _GPGSA(fields):
    # GPS satelite data and whether locked or not
    pass
def _GPRMC(fields):
    _set_time(fields[1])
    _set_lat_long(fields[3],fields[4],fields[5], fields[6])
    _set_speed(fields[7])
    _set_dir(fields[8])
def _GPGSV(fields) :
    # GPS satelite data and quality
    pass
def _GPVTG(fields):
    _set_speed(fields[3])
    _set_dir(fields[1])

_func = {'$GPVTG': _GPVTG,
            '$GPGGA': _GPGGA,
            '$GPGLL': _GPGLL,
            '$GPGSA': _GPGSA,
            '$GPRMC': _GPRMC,
            '$GPGSV': _GPGSV}

def Check():
    global _Port
    global Connected
    global _Buffer

    if not Connected :
        return

    count = _Port.inWaiting()
    if (count > 0) :
        buff = _Port.read(size=count)
        _Buffer = _Buffer + buff
        
    start = _Buffer.find('$')
    if start == -1 :
        _Buffer = ''
        return
    while start > 0 :
        end = _Buffer.find('\r',start)
        if end == -1 :
            return
        
        line = _Buffer[start:end]
        _Buffer = _Buffer[end:]

        if len(line) < 5 :
            return
        if not _valid_msg(line) :
            writeLog(LOG_ERROR, 'GPS checksum error ' + line)
            return

        writeLog(LOG_GPS_RAW, line)
        fields = line.split(',')
    
        try :
            _func[fields[0]](fields)
        except KeyError as err :
            writeLog(LOG_ERROR, 'unknown GPS command: '+line)

        start = _Buffer.find('$')
