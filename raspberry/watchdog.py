from log import *
import Arduino
import subprocess
import time

Arduino_Port = '/dev/ttyACM0'
log_path = 'logs/logs-watchdog.txt'
interval = 5
last_poll = 0

openFile(log_path)

def stop_it() :    
    Arduino.open(Arduino_Port)
    Arduino._serial_cmd(Arduino._Commands["speed"], 0)
    Arduino._serial_cmd(Arduino._Commands["steer"], 0)

def poll() :
    writeLog(LOG_WATCHDOG, 'WatchDog Checking')
    if 'python controller.py' in subprocess.check_output(['ps','u']) :
        writeLog(LOG_WATCHDOG, 'Controler is still running')
    else :
        writeLog(LOG_WATCHDOG, 'Controler has stoped')
        stop_it()

while(1):
    global interval
    
    time.sleep(interval)
    poll()
