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
        _Port = serial.Serial(port, 4800, timeout=0)
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

'''
def haversine(lon1, lat1, lon2, lat2) :
    lon1 = radians(lon1)
    lat1 = radians(lat1)
    lon2 = radians(lon2)
    lat2 = radians(lat2)

    dLat = lat2 - lat1
    dLon = lon2 - lon1

    a = sin((dLat/2)**2 + cos(lat1) * cos(lat2) * (dLon/2)**2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = 6371 * c

    return d * 3280.8399'''

'''#calculates the distance between two gps coordinates returns ft
def haversine(lon1, lat1, lon2, lat2) :
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km * 3280.8399 '''

def bearing(lat1, lon1, lat2, lon2) :
    #lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    y = sin(dLon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
    bearing = degrees(atan2(y,x))

    return bearing

'''
def bearing(lat1, lon1, lat2, lon2) :
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dPhi = log(tan(lat2/2.0 + pi/4.0)/tan(lat1/2.0 + pi/4.0))
    if abs(dlon) > pi :
        dlon = -(2.0 * pi - dlon)
    else :
        dlon = (2.0 * pi + dlon)

    return (degrees(atan2(dlon, dPhi)) + 360.0) % 360.0
'''

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
    global old_Latitude
    global old_Longitude
    global Latitude
    global Longitude

    if not Connected :
        return

    old_Latitude = Latitude
    old_Longitude = Longitude

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
