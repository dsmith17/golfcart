from log import *
import Arduino
import subprocess
import time

Arduino_Port = '/dev/ttyACM0'
interval = 30
last_poll = 0

def stop_it() :    
    Arduino.open(Arduino_Port)
    Arduino._serial_cmd(Arduino._Commands["speed"], 0)
    Arduino._serial_cmd(Arduino._Commands["steer"], 0)

def poll() :
    global last_poll
    
    if last_poll + interval > time.time() :
        return
    last_poll = time.time()    
    writeLog(LOG_ALWAYS, 'WatchDog Watching')
    if 'python controller.py' in subprocess.check_output(['ps','u']) :
        writeLog(LOG_ALWAYS, 'We\'re ok')
    else :
        writeLog(LOG_ALWAYS, 'It\'s dead Jim')
        stop_it()

while(1):
    poll()
