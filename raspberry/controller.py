# needs requests module from http://docs.python-requests.org/en/latest/
import requests
import io
import time
import serial #Has to be installed from pyserial.sourceforge.net/
from log import *
import GPS

url = 'http://157.182.184.52/~agc/command.php'
GPS_port = 'COM17'

Commands = {"steer": "4", "speed" : "5", "brake" : "6",
            "dir" : "7", "steer mode" : "8"}
ARDUINO_STATUS = 9
ArduinoConnected = False

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
    GPS.checkGPS()
    checkArduinoStatus()
    time.sleep(0.55)

# Ping the server once to get current Sequence
writeLog(LOG_ALWAYS, 'AGC Startup')
if ArduinoConnected :
    line = arduino_resp()
GPS.open(GPS_port)
pingServer(sequence_only=True)
writeLog(LOG_ALWAYS, 'AGC Startup: seq='+str(Sequence))
while(1):
    poll()
