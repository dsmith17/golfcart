import io
import time

# Log file records timestamped activity. Data being logged can be controlled
# by setting logMask and logConsoleMask
logFile = open('log-PythonClient.txt', 'w')
LOG_PING_SERVER = 0x00000001
LOG_NEW_COMMAND = 0x00000002
LOG_SERIAL_OUT  = 0x00000004
LOG_SERIAL_IN   = 0x00000008
LOG_SERIAL_ERROR= 0x00000010
LOG_PING        = 0x00000020
LOG_SEQ_ERROR   = 0x00000040
LOG_GPS_RAW     = 0x00001000
LOG_GPS_POS     = 0x00002000
LOG_GPS_DIR     = 0x00004000
LOG_GPS_SPEED   = 0x00008000
LOG_GPS_TIME    = 0x00010000
LOG_DETAILS     = 0x40000000
LOG_ERROR       = 0x80000000
LOG_ALWAYS      = 0xFFFFFFFF
logMask         = 0xFFFFFFFF & ~(LOG_PING_SERVER)
logConsoleMask  = 0xFFFFFFFF & ~(LOG_PING_SERVER | LOG_GPS_RAW)

def writeLog(mask, msg):
    global logFile
    global logMask
    global Pings
    global Sequence

    curTime = time.time()
    outMsg = time.ctime(curTime) + ' ' + str(msg)
    if mask & logMask :
        logFile.write(outMsg + '\n')
        logFile.flush()
    if mask & logConsoleMask :
        print outMsg

