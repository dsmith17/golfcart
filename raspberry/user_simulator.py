#  needs requests module from http://docs.python-requests.org/en/latest/
import requests
import io
import time
import random

url = 'http://157.182.184.52/~agc/control.php'

Pings = 0

# Log file records timestamped activity. Data being logged can be controlled
# by setting logMask and logConsoleMask
logFile = open('userSimulator.log', 'w')
LOG_PING_SERVER = 0x00000001
LOG_NEW_COMMAND = 0x00000002
LOG_SERIAL_OUT  = 0x00000004
LOG_SERIAL_IN   = 0x00000008
LOG_DETAILS     = 0x40000000
LOG_ERROR       = 0x80000000
LOG_ALWAYS      = 0xFFFFFFFF
logMask         = 0xFFFFFFFF
logConsoleMask  = 0xFFFFFFFF
def writeLog(mask, msg):
    global logFile
    global logMask
    global Pings
    if mask & logMask :
        curTime = time.time()
        outMsg = time.asctime() + ' Pings ' + str(Pings) + ' ' + str(msg)
        logFile.write(outMsg + '\n')
        logFile.flush()
        if mask & logConsoleMask :
            print outMsg

def issueCommand(command):
    global LOG_PING_SERVER
    global LOG_ERROR
    global Pings
    global Session

    Pings += 1

    formattedUrl = url + '?command=' + command # + '&seq=' + str(Pings)

    #params = {'command' : command}
    try :
        #resp = Session.get(url, data=params, timeout=1.0).text
        resp = Session.get(formattedUrl, timeout=1.0).text
        writeLog(LOG_PING_SERVER, 'Poll: ' + command)
    except requests.HTTPError as err :
        writeLog(LOG_ERROR, 'HTTP Error: ' + str(err))
    except requests.Timeout as err :
        writeLog(LOG_ERROR, 'HTTP Error: ' + str(err))

# Ping the server once to get current sequence
writeLog(LOG_ALWAYS, 'User Simulator Startup')
Session = requests.session()

issueCommand('reset')
time.sleep(2)
while(1):
    # command = random.choice(['faster', 'slower', 'left', 'right', 'stop'])
    command = random.choice(['faster', 'slower'])
    issueCommand(command)
    time.sleep(2.1)
