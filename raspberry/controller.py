from log import *
import GPS
import Arduino
import Server

url = 'http://157.182.184.52/~agc/command.php'
GPS_Port = 'COM17'
Arduino_Port = 'COM6'

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
Server.Ping(sequence_only=True)
while(1):
    poll()
