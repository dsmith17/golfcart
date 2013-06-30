import io
import time
import serial #Has to be installed from pyserial.sourceforge.net/
from log import *
from math import radians, degrees, cos, sin, asin, sqrt, tan, log, pi, degrees, atan2

Connected = False
_Port = ''

# Serial port used to communicate with GPS
def open(port) :
    global _Port
    global Connected
    try :
        _Port = serial.Serial(port, 57600, timeout=0)
        Connected = True
        writeLog(LOG_DETAILS, 'Connected to GPS: ' + str(port))
    except Exception as err :
        writeLog(LOG_ERROR, 'Unable to connect to GPS: ' + str(port))

Latitude = 0.0
Longitude = 0.0
old_Latitude = 0.0
old_Longitude = 0.0
Direction = 0.0
Speed = 0.0
Time = 0.0
_Buffer = ' '
Bearing = 0.0

#calculates the distance between two gps coordinates returns ft
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    
    # In kilometers
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat / 2) * sin(dLat / 2) + sin(dLon / 2) * sin(dLon / 2) * cos(lat1) * cos(lat2)
    c = 2 * asin(sqrt(a))
    return R * c * 3280.8399

def bearing(lat1, lon1, lat2, lon2) :
    #lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    y = sin(dLon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
    bearing = degrees(atan2(y,x))

    #writeLog(LOG_DETAILS, 'This is a bearing : ' + repr(bearing))
    return bearing

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
    try :
        new_time = float(val)
    except ValueError :
        writeLog(LOG_ERROR, 'Got a bad float conversion')
        new_time = Time
    if new_time != Time :
        Time = new_time
        writeLog(LOG_GPS_TIME, 'GPS time: ' + str(Time))

def _set_lat_long(lat, lat_hemi, longt, longt_hemi) :
    global Latitude
    global Longitude
    global old_Latitude
    global old_Longitude
    global Bearing
    
    if len(lat) == 0 or len(longt) == 0 :
        return
    try :
        new_lat = float(lat[0:2]) + float(lat[2:])/60
        if lat_hemi == 'S' :
            new_lat = -new_lat
    except ValueError :
        writeLog(LOG_ERROR, 'Got a bad float conversion')
        new_lat = Latitude

    try :
        new_long = float(longt[0:3]) + float(longt[3:])/60
        if longt_hemi == 'E' :
            new_long = -new_long
    except ValueError :
        writeLog(LOG_ERROR, 'Got a bad float conversion')
        new_long = Longitude
        
    if new_lat != Latitude or new_long != Longitude :
        writeLog(LOG_GPS_POS, 'GPS pos: ' + str(new_lat) + ' ' + str(new_long))
        #Bearing = bearing(Latitude,Longitude,new_lat,new_long)
        #print('This is a new Bearing: ' + repr(Bearing))
        old_Latitude = Latitude
        old_Longitude = Longitude
        Latitude = new_lat
        Longitude = new_long
    
def _set_speed(val) :
    global Speed
    if len(val) != 0 :
        try :
            new_speed = float(val)
        except ValueError :
            writeLog(LOG_ERROR, 'Got a bad float conversion')

        if new_speed != Speed :
            writeLog(LOG_GPS_SPEED, 'GPS speed: ' + str(new_speed))
            Speed = new_speed
def _set_dir(val) :
    global Direction
    if len(val) != 0 :
        try :
            new_dir = float(val)
        except ValueError :
            writeLog(LOG_ERROR, 'Got a bad float conversion')
            new_dir = Direction
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
    global old_Latitude
    global old_Longitude
    global Latitude
    global Longitude

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
