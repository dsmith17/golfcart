from log import *
import GPS
import Arduino
import Server
import script
import subprocess

url = 'http://157.182.184.52/~student1/command.php'
# GPS_Port = 'COM17'
GPS_Port = '/dev/ttyUSB0'
# Arduino_Port = 'COM6'
Arduino_Port = '/dev/ttyACM0'
Script_Path = 'script.txt'
Script_mode = False

def Init_Mode() :
    global Auto_mode
    global Script_Path
    
    return_code = subprocess.call(['ping','-c','5','157.182.184.52'])
    if return_code == 1 :
        Script_mode = True
        script.read(Script_Path)
    else :
        Server.open(url)

def  poll():
    if Script_mode == False:
        Server.Ping()
    GPS.Check()
    Arduino.Check()
    script.Check()
    time.sleep(0.55)

# Ping the server once to get current Sequence
writeLog(LOG_ALWAYS, 'AGC Startup')
Init_mode()
Arduino.open(Arduino_Port)
GPS.open(GPS_Port)
#script.read(Script_Path)

while(1):
    poll()
