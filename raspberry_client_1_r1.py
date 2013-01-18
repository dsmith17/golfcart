import urllib
import serial #Has to be installed from pyserial.sourceforge.net/
import io
import termios, fcntl, sys, os

# The comFile.txt will be updated every time the user presses
# a button on the web page this is the url to that file
url = 'http://157.182.184.52/~student1/data/comFile.txt'

# The serial library is a third party called pyserial
# is allows a object to be used to talk to the arduino
# this doesn't not take into acount the tty file changeing
# name which sometimes happens
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

# The speed of the golf cart in units
# It's positive if going forward and negative for backwards
# The units are no indication of accual speed. The Arduino
# has a set speed to increase for every unit
accel = 0
accelUnit = 100
accelMin = 1000
forward = True

steerAngle = 0

command = []
sequence = 0

def pingServer():
    responce = urllib.urlopen(url)
    bob = responce.read()
    bob = bob.split()
    return bob

def writeSerial(command):
    global accel
    global accelUnit
    global accelMin
    global steerAngle
    global forward
    if command[1] == 'up':
        #if accel < 0:
        #    forward = True
        #    switchDirections()
        #accel = accel + accelUnit
        #accelerate(accel)
        if accel == 0
            accel = accelMin
        accel = accel + accelUnit
        #if accel > 0 and not(forward):
        #    switchDirections()
        accelerate(1250)
    elif command[1] == 'down':
        if accel == 0
            accel = -accelMin
        accel = accel - accelUnit
        #if accel < 0 and forward:
        #   switchDirections()
        accelerate(-1250)
    elif command[1] == 'left':
        steerAngle = steerAngle - 1;
        steering(steerAngle)
    elif command[1] == 'right':
        steerAngle = steerAngle + 1;
        steering(steerAngle)
    elif command[1] == 'stop':
        stop()

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

#def switchDirections():
#	global forward
#	global accel
##	accel = 0
#	if forward:
#		ser.write("7, 1;")
#		forward = False
#	else:
#		ser.write("7, 0;")
#		forward = True

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
        sequence = command[0]

while(1):
    poll()
