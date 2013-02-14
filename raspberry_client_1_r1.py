import urllib
import serial #Has to be installed from pyserial.sourceforge.net/
import io
import termios, fcntl, sys, os

# The comFile.txt will be updated every time the user presses
# a button on the web page this is the url to that file
url = 'http://157.182.184.52/~student1/data/comFile.txt'
postUrl = "http://157.182.184.52/~student1/control2.php"
params = urllib.urlencode({'accel': 0, 'steer': 0, 'brake': True})

# The serial library is a third party called pyserial
# is allows a object to be used to talk to the arduino
# this doesn't not take into acount the tty file changeing
# name which sometimes happens
#ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser = serial.Serial('COM3', 115200, timeout=1)

# The log file will record the average delay in milliseconds
# between each recived command as well as the longest and shortest
# intervals.
logFile = open('log-PythonClient.txt', 'w')
longestWebTime = 0
webTime = 0
countWeb = 0
serialTime = 0
countSerial = 0

# The speed of the golf cart in units
# It's positive if going forward and negative for backwards
# The units are no indication of accual speed. The Arduino
# has a set speed to increase for every unit
accel = 0
accelUnit = 100
accelMin = 1150
accelMax = 4000
forward = True

steerAngle = 0
steerUnit = 10

command = []
sequence = 0

def pingServer():
    global webTime
    global longestWebTime
    global countWeb
    global logFile
    curTime = time.time()
    responce = urllib.urlopen(url)
    bob = responce.read()
    bob = bob.split()
    endTime = time.time()
    webTime = webTime + (endTime - curTime)
    if (endTime - curTime) > longestWebTime:
        longestWebTime = endTime - curTime
    countWeb = countWeb + 1
    out = 'A {} was recevied at {!r}\n'.format(bob[0], endTime)
    logFile.write(out)
    return bob

def writeSerial(command):
    global accel
    global accelUnit
    global accelMin
    global accelMax
    global steerAngle
    global steerUnit
    global forward
    global countSerial
    global logFile
    curTime = time.time()
    if command[1] == 'up':
        # Let the arduino handle the brake and switching directions
        if accel < accelMin
            accel = accelMin
        else
            accel = accel + accelUnit
        accelerate(accel)
        logCom = 'up'
    elif command[1] == 'down':
        if accel > -accelMin
            accel = -accelMin
        else
            accel = accel - accelUnit
        accelerate(accel)
        logCom = 'down'
    elif command[1] == 'left':
        steerAngle = steerAngle - ;
        steering(steerAngle)
        logCom = 'left'
    elif command[1] == 'right':
        steerAngle = steerAngle + 1;
        steering(steerAngle)
        logCom = 'right'
    elif command[1] == 'stop':
        stop()
        logCom = 'stop'
    endTime = time.time()
    serialTime = serialTime + (endTime - curTime)
    countSerial = countSerial + 1
    logFile.write('Wrote {} to the Arduin\n'.format(logCom))

def serialRead()
    line = ser.readline()
    args = line.split(' ')
    params = urllib.urlencode({'accel': args[0],'steer': agrs[1],'brake': args[2]})
    urllib.urlopen(responceUrl, params)

def accelerate(speed):
    ser.write("5, "+str(speed)+";")
    print("Accel "+str(speed))

def steering(angle):
    ser.write("4, "+str(angle)+";")
    print("Steer "+str(angle))

def stop():
    global accel
    ser.write("6;")
    accel = 0
    print("Stop")

def resetArduino():
    ser.setDTR(0)
    ser.setDTR(1)

def  poll():
    global command
    global sequence
    command = pingServer()
    #print(command)
    #print(command[1])
    if command[0] > sequence:
        writeSerial(command)
        serialRead()
        sequence = command[0]
    time.sleep(0.1)

while(1):
    poll()
