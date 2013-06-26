import io
import time
import serial #Has to be installed from pyserial.sourceforge.net/
from log import *

_Commands = {"steer": "4", "speed" : "5", "brake" : "6",
            "dir" : "7", "steer mode" : "8"}
_ARDUINO_STATUS = 9
Connected = False

# status variables
Speed = 0
Speed_Start = 1200
Steer = 0
Steer_current = 0
Direction = 0
Brake = 0
Steer_Mode = 0 
Steer_Step = 45
Speed_Step = 500
Speed_First = 1200

_Sequence = 0
_Port = ''
_timeLastStatus = 0    
# Serial port used to communicate with the Arduino
#Arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
def open(port) :
    global _Port
    global Connected
    try :
        _Port = serial.Serial(port, 115200, timeout=1)
        Connected = True
        writeLog(LOG_ALWAYS, 'Connected to Arduino: ' + str(port))
	sleep(2)
        _resp()
    except Exception as err :
        writeLog(LOG_ERROR, 'Unable to connect to Arduino: ' + str(port))


def Check():
    global _timeLastStatus

    # don't ping too often 
    curTime = time.time()
    if curTime - _timeLastStatus < 300 :
        return
    Get_Status()
    
def _resp() :
    line = _Port.readline()
    writeLog(LOG_SERIAL_IN, 'Serial input: '+ line)
    #line.strip()
    index = line.rfind(';')
    if index != -1 :
        line = line[:index+1]
    writeLog(LOG_SERIAL_IN, 'Serial input: '+ line)
    return line

def _reset():
    global _Port

    _Port.setDTR(0)
    _Port.setDTR(1)
    line = _resp()

def _serial_cmd(cmd, param) :
    global _Port
    global _Sequence

    if not Connected :
        return
 
    _Sequence = _Sequence + 1
    command = str(cmd) + ', ' + str(_Sequence) + ', ' + str(param) + ';'
    _Port.write(command)
    writeLog(LOG_SERIAL_OUT, 'Serial out: ' + command)
    line = _resp()
    args = line.split(',')
    if str(cmd) != args[0] or str(_Sequence) != args[1] :
        writeLog(LOG_SERIAL_ERROR, "Serial Resp Mismatch: " + str(cmd) + " " + args[0] + " " + str(_Sequence) + " " + args[1])
def Get_Status() :
    global _timeLastStatus
    global _Port
    global _Sequence
    global Speed
    global Steer_current
    global Direction
    global Brake
    global Steer_Mode

    if not Connected :
        return
    
    _Sequence = _Sequence + 1
    command = str(_ARDUINO_STATUS) + ', ' + str(_Sequence) + ';'
    _Port.write(command)
    writeLog(LOG_SERIAL_OUT, 'Serial out: ' + command)
    line = _resp()
    args = line.split(',')
    if len(args) < 2 :
        writeLog(LOG_SERIAL_ERROR, "Serial error: Too few args: " + str(line))
    elif str(_ARDUINO_STATUS) != args[0] or str(_Sequence) != args[1] :
        writeLog(LOG_SERIAL_ERROR, "Serial Resp Mismatch: " + str(command) + " " + args[0] + " " + str(_Sequence) + " " + args[1])
    else :
        Steer_current       = int(args[2])
        Speed               = int(args[3])
        Direction           = int(args[4])
        Brake               = int(args[5])
        Steer_Mode          = int(args[6])
    _timeLastStatus         = time.time()
def _cmd_reset() :
    global _Sequence
    writeLog(LOG_DETAILS, 'reset Sequence number')
    _Sequence = 0

def Execute(command) :
    global Steer
    global Steer_Step
    global Speed
    global Speed_Step
    global Speed_First
    global _Commands
    global _Sequence
    global Direction

    if not Connected :
        return

    if command[1] == 'right' :
        Steer += Steer_Step
        _serial_cmd(_Commands["steer"], Steer)
    elif command[1] == 'left' :
        Steer -= Steer_Step
        _serial_cmd(_Commands["steer"], Steer)
    elif command[1] == 'up' :
        if(Speed < Speed_First):
            Speed = Speed_First
        else:
            Speed += Speed_Step
        _serial_cmd(_Commands["speed"], Speed)
    elif command[1] == 'down' :
        Speed -= Speed_Step
        if Speed < 0 :
            Speed = 0
        _serial_cmd(_Commands["speed"], Speed)
    elif command[1] == 'stop' :
        Speed = 0
        _serial_cmd(_Commands["speed"], Speed)
    elif command[1] == 'reload' :
        pass
    elif command[1] == 'reset' :
        _cmd_reset()
    elif command[1] == 'change_direction' :
        if Direction == 0 :
            Direction = 1
        else :
            Direction = 0
        Speed = 0
        _serial_cmd(_Commands["speed"], Speed)
        _serial_cmd(_Commands["dir"], Direction)
    elif command[1] == 'steer mode' :
        _serial_cmd(_Commands["steer mode"], command[2])
    else :
        writeLog(LOG_ERROR, 'Unknown command: ' + str(command))
    
