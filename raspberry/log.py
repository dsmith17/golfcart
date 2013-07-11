
import io
import time

# Log file records timestamped activity. Data being logged can be controlled
# by setting logMask and logConsoleMask
logFile = open('logs/log-PythonClient.txt', 'a')
#watchFile = open('logs/log_watchdog.txt', 'a')
#gps_pos = open('logs/log-Gps_Position.txt', 'a')
#gps_dir = open('logs/log_Gps_Direction.txt', 'a')
#gps_raw = open('logs/log_Gps_Raw_Data.txt', 'a')

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
LOG_WATCHDOG    = 0x00100000
LOG_DETAILS     = 0x40000000
LOG_ERROR       = 0x80000000
LOG_ALWAYS      = 0xFFFFFFFF

logMask         = 0xFFFFFFFF
logConsoleMask  = 0xFFFFFFFF
'''logMask         = 0xFFFFFFFF & ~(LOG_PING_SERVER | LOG_GPS_RAW | LOG_GPS_TIME | LOG_GPS_POS
                                 | LOG_GPS_SPEED | LOG_GPS_DIR)
logConsoleMask  = 0xFFFFFFFF & ~(LOG_PING_SERVER | LOG_GPS_RAW | LOG_GPS_TIME | LOG_GPS_POS
                                 | LOG_GPS_SPEED | LOG_GPS_DIR)
#logGPS_POS_Mask = 0x0000F000 & ~(LOG_GPS_SPEED | LOG_GPS_DIR | LOG_GPS_RAW)
#logGPS_DIR_Mask = 0x0000F000 & ~(LOG_GPS_SPEED | LOG_GPS_POS | LOG_GPS_RAW)
#logGPSMask      = 0x000FF000
#logWatchMask    = 0x00F00000'''

def openFile(filepath):
    logFile.close()
    logFile = open(filepath);

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
'''    if mask & logGPSMask :
        gps_raw.write(outMsg + '\n')
        gps_raw.flush()
    if mask & logGPS_DIR_Mask :
        gps_dir.write(outMsg + '\n')
        gps_dir.flush()
    if mask & logGPS_POS_Mask :
        gps_pos.write(outMsg + '\n')
        gps_pos.flush()
    if mask & logWatchMask :
        watchFile.write(outMsg + '\n')
        watchFile.flush()'''

