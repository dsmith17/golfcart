from log import *
import GPS
import Arduino
import Server

Auto_mode = False

Instruction_num = 0
Command = [0,'',0] #index, instruction, paramater
_Script = ''
_file = ''
start_Lat = 0.0
start_Lon = 0.0

MAX_FORWARD_FT = 999
delta_Distance = 3
Moving_Forward = False
current_Distance = 0.0
end_Distance = 0

Turning_To = False
Turning_Delta = False
Turning_Delta_Init = False
Turn_Delta_Angle = 0
delta_Turning = 4
prec_Turning = 1
angle_Turning = 0
_degrees = 500*(1000/360)
end_bearing = 0
bearing = 0

Delaying = False
delay_time = 0
delay_length = 0



def execute_Command(instruct, parm) :
    global Command
    global Instruction_num

    Instruction_num = Instruction_num + 1
    Command[0] = Instruction_num
    Command[1] = instruct
    Command[2] = parm

    Arduino.Execute(Command)

def read(path) :
    global _Script
    global Command

    _Script = open(path, 'r')
    Auto_mode = True
    execute_Command('steer mode', 0)

def start_auto(file_buf) :
    global _Script
    global Command
    global Auto_mode
    
    _Script = file_buf
    Auto_mode = True
    writeLog(LOG_SERIAL_IN, 'This is the file :\n' + _Script)
    #execute_Command('steer mode', 0)

def Check() :
    global _Script
    global start_Lat
    global start_Lon
    global current_Distance
    global end_Distance
    global delta_Distance
    global Moving_Forward
    global Turning_To
    global Turning_Delta
    global Auto_mode
    global Turn_Delta_Angle
    global Turning_Delta_Init
    global Turn_To_Angle
    global _degrees
    global end_bearing
    global bearing
    global prec_Turning
    global delta_Turning
    global old_latitude
    global old_longitude
    global Delaying
    global delay_time
    global delay_length

    #writeLog(LOG_SERIAL_IN, 'Script checking')    
    if Auto_mode :
        #line = _Script.readlines()
        line = 'yes'
        #writeLob(LOG_SERIAL_IN, 'In Auto_mode')
        if line != '' :
            writeLog(LOG_SERIAL_IN, 'Executing script')
            Auto_mode = False
            execute(_Script)
        else :
            writeLog(LOG_SERIAL_IN, 'Didn\'t execute script')
            Auto_mode = False
            execute_Commmand('steer mode', 1)
    else :
        if Moving_Forward :
            #if GPS.old_Latitude != GPS.Latitude or GPS.old_Longitude != GPS.Longitude :
            #writeLog(LOG_SERIAL_IN, 'Old_lat, lat, Old.Long, Long : ' + GPS.old_Latitude + ' ,' + GPS.Latitude + ' ,' + GPS.old_Longitude + ' ,' + GPS.Longitude)
            writeLog(LOG_SERIAL_IN, 'Old distance' + repr(current_Distance))
            current_Distance = GPS.haversine(start_Lat, start_Lon, GPS.Latitude, GPS.Longitude)
            writeLog(LOG_SERIAL_IN, 'New distance' + repr(current_Distance))
            if current_Distance >= end_Distance - delta_Distance and current_Distance < end_Distance :
                Arduino._serial_cmd(Arduino._Commands["speed"], 1500)
            elif current_Distance >= end_Distance :
                Arduino._serial_cmd(Arduino._Commands["speed"], 0)
                Moving_Forward = False
                Auto_mode = True
                _Script = ''
        if Turning_To :
            if Moving_Forward == False :
                bearing = GPS.bearing(start_Lat, start_Lon, GPS.Latitude, GPS.Longitude)
                if Turn_To_Angle > bearing :
                    if Turn_To_Angle - bearing > 180 : #Turn left
                        #bearing = -1*((360 - Turn_To_Angle) + bearing)
                        Arduino._serial_cmd(Arduino._Commands["steer"], -1*_degrees)
                    else : #Turn right
                        Arduino._serial_cmd(Arduino._Commands["steer"], _degrees)
                        #bearing = Turn_To_Angle - bearing
                else :
                    if bearing - Turn_To_Angle > 180 : #Turn right
                        Arduino._serial_cmd(Arduino._Commands["steer"], _degrees)
                        #bearing = (360 - bearing) + Turn_To_Angle
                    else : #Turn Left
                        Arduino._serial_cmd(Arduino._Commands["steer"], -1*_degrees)
                        #bearing = Turn_To_Angle - bearing
                Arduino._serial_cmd(Arduino._Commands["speed"], 1700)
                Turning_Delta_Init = False
                old_latitude = GPS.Latitude
                old_longitude = GPS.Longitude
                end_bearing = Turn_To_Angle
                Turning_Delta = True
                Turning_To = False
        if Turning_Delta :
            if Moving_Forward == False and Turning_Delta_Init == True :
                bearing = GPS.bearing(start_Lat, start_Lon, GPS.Latitude, GPS.Longitude)
                end_bearing = Turn_Delta_Angle + bearing
                print('This is a bearing : ' + bearing)
                if Turn_Delta_Angle > 0 :
                    Arduino._serial_cmd(Arduino._Commands["steer"], _degrees)
                else :
                    Arduino._serial_cmd(Arduino._Commands["steer"], -1*_degrees)
                Arduino._serial_cmd(Arduino._Commands["speed"], 1700)
                Turning_Delta_Init = False
                old_latitude = GPS.Latitude
                old_longitude = GPS.Longitude
            elif Moving_Forward == False and Turning_Delta_Init == False :
                bearing = GPS.bearing(old_latitude, old_longitude, GPS.Latitude, GPS.Longitude)
                old_latitude = GPS.Latitude
                old_longitude = GPS.Longitude

                #if bearing < end_bearing : #on the right side of bearing
                if Turn_Delta_Angle > 0 : #Turning right
                    if bearing < 
		    if end_bearing - bearing < prec_Turning : #stop turning
                        Arduino._serial_cmd(Arduino._Commands["speed"], 0)
                        Arduino._serial_cmd(Arduino._Commands["steer"], 0)
                        Turning_Delta = False
                        Auto_mode = True
                        _Script = ''
                    elif end_bearing - bearing < delta_Turning :
                        Arduino._serial_cmd(Arduino._Commands["speed"], 1500)
                #elif bearing > end_bearing : #on the left side of bearing
                else : #Turning left
                    if bearing - end_bearing < prec_Turning : #stop turning
                        Arduino._serial_cmd(Arduino._Commands["speed"], 0)
                        Arduino._serial_cmd(Arduino._Commands["steer"], 0)
                        Turning_Delta = False
                        Auto_mode = True
                        _Script = ''
                    elif bearing - end_bearing < delta_Turning : #slow
                        Arduino._serial_cmd(Arduino._Commands["speed"], 1500)
                    
def execute(line) :
    global start_Lat
    global start_Lon
    global end_Distance
    global Auto_mode
    global Moving_Forward
    global MAX_FORWARD_FT
    global Turning_Delta
    global Turning_Delta_Init
    global Turn_Delta_Angle
    global Turning_To
    global Turn_To_Angle
    global Delaying
    global delay_start
    global delay_length

    #Format line
    line = line.rstrip(';')
    #print(line)
    parm = line.split(',')
    #print(parm)
    writeLog(LOG_SERIAL_IN, parm)
    
    # Lets golfcart drift to a stop w/o brake
    if 'Soft Stop' in line :
        Arduino._serial_cmd(Arduino._Commands["speed"], 0)
        
    # Applies brake to stop
    elif 'Hard Stop' in line :
        Arduino._serial_cmd(Arduino._Commands["speed"], 0)
        Arduino._serial_cmd(Arduino._Commands["brake"], 1)
        
    # Go forward up to MAX_FORWARD_FT ft
    elif 'Move Forward' == parm[0] :
        print('Got Move Forward')
        parm1 = int(parm[1])
        if parm1 > MAX_FORWARD_FT :
            parm1 = MAX_FORWARD_FT
        Moving_Forward = True
#        execute_Command('up',0)
#        execute_Command('up',0)
        Arduino._serial_cmd(Arduino._Commands["speed"], 1700)
        Auto_mode = False
        start_Lat = GPS.Latitude
        start_Lon = GPS.Longitude
        end_Distance = parm1

    # Turn to a specified compass heading
    elif 'Turn To' == parm[0] :
        print('Got Turn To')
        Turning_To = True
        parm1 = int(parm[1])
        Turn_To_Angle = parm1
        execute('Moving Forward,5;')

    # Turn a number of degrees
    elif 'Turn Delta' == parm[0] :
        print('Got Turn Delta')
        parm1 = int(parm[1])
        Turning_Delta = True
        Turning_Delta_Init = True
        Turn_Delta_Angle = parm1
        execute('Moving Forward,5;')
        

#    elif 'Follow Heading' in line :

#    elif 'Follow Course' in line :

#    elif 'Control Speed' in line :

    elif 'Delay' in line :
        print('Got Delay')
        parm1 = int(parm[1])
        Delaying = True
        delay_length = parm1
#        delay_start = 
    
