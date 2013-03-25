# needs requests module from http://docs.python-requests.org/en/latest/
import requests
#import urllib2
import io
import time
import serial #Has to be installed from pyserial.sourceforge.net/
#import termios, fcntl, sys, os

url = 'http://157.182.184.52/~agc/command.php'

Commands = {"steer": "4", "speed" : "5", "brake" : "6",
            "dir" : "7", "steer mode" : "8"}
ARDUINO_STATUS = 9
ArduinoConnected = False
GPSConnected = False

# status variables
Speed = 0
Steer = 0
Direction = 0
Brake = 0
Steer_Mode = 0

Pings = 0
Arduino_Sequence = 0
# session used to communicate with server
Session = requests.session()

# Serial port used to communicate with the Arduino
#Arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
try :
    Arduino = serial.Serial('COM6', 115200, timeout=1)
    ArduinoConnected = True
except Exception as err :
    print 'Unable to connect to Arduino'

# Serial port used to communicate with GPS
try :
    GPS = serial.Serial('COM17', 4800, timeout=0)
    GPSConnected = True
except Exception as err :
    print 'Unable to connect to GPS'

GPS_lat = 0.0
GPS_long = 0.0
GPS_dir = 0.0
GPS_speed = 0.0
GPS_time = 0.0
GPS_Buffer = ' '

# Log file records timestamped activity. Data being logged can be controlled
# by setting logMask and logConsoleMask
logFile = open('log-PythonClient.txt', 'w')
LOG_PING_SERVER = 0x00000001
LOG_NEW_COMMAND = 0x00000002
LOG_SERIAL_OUT  = 0x00000004
LOG_SERIAL_IN   = 0x00000008
LOG_SERIAL_ERROR= 0x00000010
LOG_PING        = 0x00000020
LOG_SEQ_ERROR   = 0x00000040
LOG_GPS_RAW     = 0x00001000
LOG_GPS_POS     = 0x00002000
LOG_GPS_DIR     = 0x00004000
LOG_GPS_SPEED   = 0x00008000
LOG_GPS_TIME    = 0x00010000
LOG_DETAILS     = 0x40000000
LOG_ERROR       = 0x80000000
LOG_ALWAYS      = 0xFFFFFFFF
logMask         = 0xFFFFFFFF & ~(LOG_PING_SERVER)
logConsoleMask  = 0xFFFFFFFF & ~(LOG_PING_SERVER | LOG_GPS_RAW)

def writeLog(mask, msg):
    global logFile
    global logMask
    global Pings
    global Sequence

    curTime = time.time()
    outMsg = time.ctime(curTime) + ' P:' + str(Pings) + ' S:' + str(Sequence) + ' ' + str(msg)
    if mask & logMask :
        logFile.write(outMsg + '\n')
        logFile.flush()
    if mask & logConsoleMask :
        print outMsg

def formatUrl():
    formattedUrl = url + '?speed='+str(Speed) + '&steer='+str(Steer)
    if Direction :
        formattedUrl += '&direction=BACK'
    else :
        formattedUrl += '&direction=FORWARD'
        
    if Brake :
        formattedUrl += '&brake=ON'
    else :
        formattedUrl += '&brake=OFF'

    if Steer_Mode :
        formattedUrl += '&steermode=ACTIVE'
    else :
        formattedUrl += '&steermode=PASSIVE'
    return formattedUrl

def is_int(val) :
    try :
        intval = int(val)
        return True
    except :
        return False

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
    global GPS
    global GPSConnected
    global GPS_Buffer

    if not GPSConnected :
        return

    count = GPS.inWaiting()
    if (count > 0) :
        buff = GPS.read(size=count)
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


timeLastPing = 0    
def pingServer(sequence_only=False):
    global Sequence
    global Pings
    global timeLastPing
    global Sequence

    # don't ping too often or the server gets crabby
    curTime = time.time()
    if curTime - timeLastPing < 0.5 :
        return
    
    Pings += 1
    
    #params = {'command' : command}
    try :
        #resp = Session.get(url, data=params, timeout=1.0).text
        command = Session.get(formatUrl(), timeout=1.0).text
        writeLog(LOG_PING_SERVER, 'Poll: ' + str(command.split()))
    except requests.HTTPError as err :
        command = str(Sequence) + ' HTTP_error'
        writeLog(LOG_ERROR, 'HTTP Error: ' + str(err))
    except requests.Timeout as err :
        command = str(Sequence) + ' HTTP_timeout'
        writeLog(LOG_ERROR, 'HTTP timeout: ' + str(err))

    commandParts = command.split()

    if (len(commandParts) != 2) or (not is_int(commandParts[0])) :
        writeLog(LOG_ERROR, 'Invalid seq ' + str(commandParts))
        return
    curTime = time.time()
    if timeLastPing != 0 and curTime > timeLastPing + 1.5 :
        writeLog(LOG_SEQ_ERROR, 'Last ping at ' + time.ctime(timeLastPing))
    timeLastPing = curTime
    
    new_seq = int(commandParts[0])
    if sequence_only :
        Sequence = new_seq
        return
    
    if new_seq > Sequence:
        if new_seq != Sequence + 1 :
            writeLog(LOG_SEQ_ERROR, 'Missed sequence number: ' + str(Sequence) + ' ' + str(new_seq))
        Sequence = new_seq
        writeLog(LOG_NEW_COMMAND, 'New command: ' + str(commandParts))
        execute(commandParts)
        get_arduino_status()
    elif commandParts[1] == 'reset' :
        cmd_reset()

timeLastStatus = 0    
def checkArduinoStatus():
    global timeLastStatus

    # don't ping too often 
    curTime = time.time()
    if curTime - timeLastStatus < 300 :
        return
    get_arduino_status()
    
def arduino_resp() :
    line = Arduino.readline()
    #line.strip()
    index = line.rfind(';')
    if index != -1 :
        line = line[:index+1]
    writeLog(LOG_SERIAL_IN, 'Serial input: '+ line)
    return line

def resetArduino():
    global LOG_SERIAL_IN
    global Arduino

    Arduino.setDTR(0)
    Arduino.setDTR(1)
    line = arduino_resp()

Steer_Step = 10
Speed_Step = 1000
def serial_cmd(cmd, param) :
    global Arduino
    global Arduino_Sequence

    Arduino_Sequence = Arduino_Sequence + 1
    command = str(cmd) + ', ' + str(Arduino_Sequence) + ', ' + str(param) + ';'
    Arduino.write(command)
    writeLog(LOG_SERIAL_OUT, 'Serial out: ' + command)
    line = arduino_resp()
    args = line.split(',')
    if str(cmd) != args[0] or str(Arduino_Sequence) != args[1] :
        writeLog(LOG_SERIAL_ERROR, "Serial Resp Mismatch: " + str(cmd) + " " + args[0] + " " + str(Arduino_Sequence) + " " + args[1])
def get_arduino_status() :
    global timeLastStatus
    global Arduino
    global Arduino_Sequence
    global Speed
    global Steer
    global Direction
    global Brake
    global Steer_Mode

    if not ArduinoConnected :
        return
    
    Arduino_Sequence = Arduino_Sequence + 1
    command = str(ARDUINO_STATUS) + ', ' + str(Arduino_Sequence) + ';'
    Arduino.write(command)
    writeLog(LOG_SERIAL_OUT, 'Serial out: ' + command)
    line = arduino_resp()
    args = line.split(',')
    if str(ARDUINO_STATUS) != args[0] or str(Arduino_Sequence) != args[1] :
        writeLog(LOG_SERIAL_ERROR, "Serial Resp Mismatch: " + str(cmd) + " " + args[0] + " " + str(Arduino_Sequence) + " " + args[1])
    else :
        Steer      = int(args[2])
        Speed      = int(args[3])
        Direction  = int(args[4])
        Brake      = int(args[5])
        Steer_Mode = int(args[6])
    timeLastStatus = time.time()
def cmd_reset() :
    global Sequence
    writeLog(LOG_DETAILS, 'reset Sequence number')
    Sequence = 0

def execute(command) :
    global Steer
    global Steer_Step
    global Speed
    global Speed_Step
    global Commands
    global Sequence

    if not ArduinoConnected :
        return

    if command[1] == 'right' :
        Steer += Steer_Step
        serial_cmd(Commands["steer"], Steer)
    elif command[1] == 'left' :
        Steer -= Steer_Step
        serial_cmd(Commands["steer"], Steer)
    elif command[1] == 'up' :
        Speed += Speed_Step
        serial_cmd(Commands["speed"], Speed)
    elif command[1] == 'down' :
        Speed -= Speed_Step
        if Speed < 0 :
            Speed = 0
        serial_cmd(Commands["speed"], Speed)
    elif command[1] == 'stop' :
        Speed = 0
        serial_cmd(Commands["speed"], Speed)
    elif command[1] == 'reload' :
        pass
    elif command[1] == 'reset' :
        cmd_reset()
    else :
        writeLog(LOG_ERROR, 'Unknown command: ' + str(command))
    
Sequence = 0
def  poll():
    pingServer()
    checkGPS()
    checkArduinoStatus()
    time.sleep(0.55)

# Ping the server once to get current Sequence
writeLog(LOG_ALWAYS, 'AGC Startup')
if ArduinoConnected :
    line = arduino_resp()
pingServer(sequence_only=True)
writeLog(LOG_ALWAYS, 'AGC Startup: seq='+str(Sequence))
while(1):
    poll()
