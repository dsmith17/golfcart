
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
    global Script_mode
    global Script_Path
    
    #return_code = subprocess.call(['ping','-c','5','157.182.184.52'])
    return_code = 0
    if return_code == 1 :
        Script_mode = True
        script.init_dir()
        script.read(Script_Path)
    else :
        Server.open(url)
    #subprocess.call(['python','watchdog.py'])

def  poll():
    GPS.Check()
    Arduino.Check()
    if Script_mode == False:
        Server.Ping()
    script.Check()
    time.sleep(0.55)

# Ping the server once to get current Sequence
writeLog(LOG_ALWAYS, 'AGC Startup')
Init_Mode()
Arduino.open(Arduino_Port)
GPS.open(GPS_Port)
#script.read(Script_Path)

while(1):
    poll()
