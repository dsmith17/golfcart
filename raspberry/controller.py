from log import *
import GPS
import Arduino
import Server

url = 'http://157.182.184.52/~student1/command.php'
# GPS_Port = 'COM17'
GPS_Port = '/dev/ttyUSB0'
# Arduino_Port = 'COM6'
Arduino_Port = '/dev/ttyACM0'

def  poll():
    Server.Ping()
    GPS.Check()
    Arduino.Check()
    time.sleep(0.55)

# Ping the server once to get current Sequence
writeLog(LOG_ALWAYS, 'AGC Startup')
Server.open(url)
Arduino.open(Arduino_Port)
GPS.open(GPS_Port)

while(1):
    poll()
