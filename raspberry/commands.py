from log import *
import time
import GPS
import Arduino
import Server

Command_Running = False
Current_Command = ''
Command_Start = time.time()     # start time of command
Delay_Time = 0                  # timeout for command
Distance = 0                    # How far we are moving
Start_Lat = 0
Start_Long = 0

_Commands = {

def Execute(command) :
    command = command.strip();
    command = command.rstrip(';')
    parm = command.split(',')
    #print(parm)
    writeLog(LOG_NEW_COMMAND, parm)

    Current_Command = parm[0]
    Command_Running = True
    Command_Start = time.time()

    if parm[0] == 'sstop' :
        Arduino._serial_cmd(Arduino._Commands["speed"], 0)
        Delay_Time = 5
    elif parm[0] == 'hstop' :
        Arduino._serial_cmd(Arduino._Commands["speed"], 0)
        Arduino._serial_cmd(Arduino._Commands["brake"], 1)
        Delay_Time = 10
    elif parm[0] == 'turnto' :
        pass
    elif parm[0] == 'turndelta' :
        pass
    elif parm[0] == 'forward' :
        Distance = parm[1]
        Start_Lat = GPS.Latitude
        Start_Long = GPS.Lonitude
        # we probably need to use Arduino.x to start moving
    elif parm[0] == 'heading' :
        pass
    elif parm[0] == 'delay' :
        Delay_Time = int(parm[1])
    else
        writeLog(LOG_ERROR, 'Unrecognized command')
        Command_Running = False

def Check() :
    global Distance
    global Command_Running
    global Current_Command
    global Delay_Time
    global Command_Start

    if not Command_Running :
        return

    if Current_Command == 'sstop' :
        GPS.Connected and GPS.Speed == 0.0 :
            Command_Running = False
        if Command_Start + Delay_Time < time.time() :
            Command_Running = False
    elif Current_Command == 'hstop' :
        # I don't know if I have the correct brake status here
        GPS.Connected and GPS.Speed == 0.0 and Arduino.Brake == 3:
            Command_Running = False
        if Command_Start + Delay_Time < time.time() :
            Command_Running = False
    elif Current_Command == 'turnto' :
        pass
    elif Current_Command == 'turndelta' :
        pass
    elif Current_Command == 'forward' :
        distance = GPS.haversine(Start_Lat, Start_Long, GPS.Latitude, GPS.Longitude)
        if distance > Distance :
            Command_Running = False
    elif Current_Command == 'heading' :
        pass
    elif Current_Command == 'delay' :
        if Command_Start + Delay_Time < time.time() :
            Command_Running = False
    else
        writeLog(LOG_ERROR, 'Unrecognized command')
        Command_Running = False



Auto_mode = False

Instruction_num = 0
Command = [0,'',0] #index, instruction, paramater
_Script = ''
_file = ''
start_Lat = 0.0
start_Lon = 0.0

MAX_FORWARD_FT = 999
delta_Distance = 1
Moving_Forward = False
current_Distance = 0.0
end_Distance = 0

old_latitude = 0.0
old_longitude = 0.0

Turning_To = False
Turn_To_Set = False
Turning_Delta = False
Turning_Delta_Init = False
Turn_Delta_Angle = 0
delta_Turning = 4
prec_Turning = 1
angle_Turning = 0
_degrees = 250*(1000/360)
end_bearing = 0
bearing = 0
old_bearing = 0
bearing_distance = 3
cur_turn_angle = 0

Delaying = False
delay_time = 0
delay_length = 0

Hard_Stopping = False

Init_Execute = False
init_start_Lat = 0.0
init_start_Lon = 0.0
init_bearing = 0.0
init_file = ''

index = 0
num_inst = 0

Heading_distance = 0
Following_Heading = 0

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
    #Auto_mode = True
    execute_Command('steer mode', 0)

def init_dir(file_buf) :
    global Init_Execute, init_start_Lat, init_start_Lon, init_script

    init_script = file_buf
    init_start_Lat = GPS.Latitude
    init_start_Lon = GPS.Longitude
    Init_Execute = True
    execute('Move Forward,10;')
    writeLog(LOG_GPS_POS, 'Init is done')

def start_auto() :
    global _Script
    global Command
    global Auto_mode
    global num_inst
    global init_file
    
    _Script = init_file.split('\n')
    num_inst = len(_Script)
    Auto_mode = True
    #writeLog(LOG_SERIAL_IN, 'This is the file :\n' + _Script[0] + '/n' + _Script[1])
    #execute_Command('steer mode', 0)
    writeLog(LOG_SERIAL_IN, 'The num of commands : ' + repr(num_inst))
    for i in range(0,num_inst) :
        writeLog(LOG_DETAILS, 'The '+repr(i)+' command is : ' + _Script[i])

def Check() :
    global _Script
    global start_Lat, start_Lon
    global current_Distance, end_Distance, delta_Distance
    global Moving_Forward
    global Turning_To, Turn_To_Angle, Turn_To_Set
    global Turning_Delta, Turn_Delta_Angle, Turning_Delta_Init
    global Auto_mode
    global _degrees
    global bearing, end_bearing, old_bearing, bearing_distance
    global prec_Turning, delta_Turning, cur_turn_angle
    global old_latitude, old_longitude
    global Delaying, delay_time, delay_length
    global Hard_Stopping
    global Init_Execute, init_start_Lat, init_start_Lon, init_bearing
    global index, num_inst
    global Heading_distance, Following_Heading


    #writeLog(LOG_SERIAL_IN, 'Script checking')    
    if Auto_mode == True and Moving_Forward == False and Turning_To == False and Turning_Delta == False and Delaying == False :
        if index+1 < num_inst :
            line = _Script[index]
            index = index + 1
        else :
            writeLog(LOG_ALWAYS, 'End of Script')
            Auto_mode = False
        #line = 'yes'
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
        if Init_Execute :
           if Moving_Forward == False:
               init_bearing = GPS.bearing(init_start_Lat, init_start_Lon, GPS.Latitude, GPS.Longitude)
               writeLog(LOG_GPS_POS, 'Initial bearing is : ' + repr(init_bearing))
               Init_Execute = False
               start_auto()
               #Auto_mode = True
               old_latitude = GPS.Latitude
               old_longitude = GPS.Longitude
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
                bearing = GPS.bearing(start_Lat, start_Lon, GPS.Latitude, GPS.Longitude)
        if Turning_To :
            if Turn_To_Set == False :
                if Turn_To_Angle > init_bearing :
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
                end_bearing = Turn_Delta_Angle + init_bearing
                print('Initial Bearing: ' + repr(init_bearing))
                #print('This is a bearing : ' + bearing)
                if Turn_Delta_Angle > 0 :
                    Arduino._serial_cmd(Arduino._Commands["steer"], _degrees)
                else :
                    Arduino._serial_cmd(Arduino._Commands["steer"], -1*_degrees)
                Arduino._serial_cmd(Arduino._Commands["speed"], 1700)
                Turning_Delta_Init = False
                print('This is the Init_Delta')
                #execute('Delay,1;')
            elif Moving_Forward == False and Turning_Delta_Init == False and Delaying == False :
                if GPS.haversine(old_latitude, old_longitude, GPS.Latitude, GPS.Longitude) < bearing_distance :
                    return
                bearing = GPS.bearing(old_latitude, old_longitude, GPS.Latitude, GPS.Longitude)
                #bearing = GPS.Direction
                writeLog(LOG_GPS_POS, 'New Bearing: ' + repr(bearing))
                old_latitude = GPS.Latitude
                old_longitude = GPS.Longitude
                #if bearing < end_bearing : #on the right side of bearing
                if Turn_Delta_Angle > 0 : #Turning right
                    if bearing < old_bearing :
                        cur_turn_angle = cur_turn_angle
                        #cur_turn_angle += (360 + bearing) - old_bearing
                    else :
                        cur_turn_angle += bearing - old_bearing
                    if Turn_Delta_Angle + delta_Turning < cur_turn_angle : #stop turning
                        Arduino._serial_cmd(Arduino._Commands["speed"], 0)
                        Arduino._serial_cmd(Arduino._Commands["steer"], 0)
                        Turning_Delta = False
                        Auto_mode = True
                        cur_turn_angle = 0
                        Turn_Delta_Angle = 0
                        init_bearing = bearing
                    elif Turn_Delta_Angle - cur_turn_angle < delta_Turning :
                        Arduino._serial_cmd(Arduino._Commands["speed"], 1500)
                #elif bearing > end_bearing : #on the left side of bearing
                else : #Turning left
                    if bearing > old_bearing :
                        cur_turn_angle = cur_turn_angle
                        #cur_turn_angle += bearing - (360 + old_bearing)
                    else :
                        cur_turn_angle += bearing - old_bearing
                    if cur_turn_angle < Turn_Delta_Angle - delta_Turning: #stop turning
                        Arduino._serial_cmd(Arduino._Commands["speed"], 0)
                        Arduino._serial_cmd(Arduino._Commands["steer"], 0)
                        Turning_Delta = False
                        Auto_mode = True
                        cur_turn_angle = 0
                        Turn_Delta_Angle = 0
                        init_bearing = bearing
                    elif Turn_Delta_Angle - cur_turn_angle < delta_Turning : #slow
                        Arduino._serial_cmd(Arduino._Commands["speed"], 1500)
        if Hard_Stopping :
            if not Delaying :
                Arduino._serial_cmd(Arduino._Commands["brake"], 0)
                Hard_Stopping = False
                Auto_mode = True
        if Delaying :
            if time.time() - delay_start > delay_length :
                Delaying = False
                Auto_mode = True

def execute(line) :
    global start_Lat, start_Lon
    global end_Distance
    global Auto_mode
    global Moving_Forward
    global MAX_FORWARD_FT
    global Turning_Delta, Turning_Delta_Init, Turn_Delta_Angle
    global Turning_To, Turn_To_Angle, Turn_To_Set
    global Delaying, delay_start, delay_length
    global Hard_Stopping
    global Heading_distance, Following_Heading

    #Format line
    line = line.strip();
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
        Hard_Stopping = True
        Delaying = True
        delay_length = 20
        delay_start = time.time()
        
    # Go forward up to MAX_FORWARD_FT ft
    elif 'Move Forward' == parm[0] :
        print('Got Move Forward of : ' + repr(parm[1]))
        parm1 = int(parm[1])
        if parm1 > MAX_FORWARD_FT :
            parm1 = MAX_FORWARD_FT
        Moving_Forward = True
        Arduino._serial_cmd(Arduino._Commands["speed"], 1700)
        Auto_mode = False
        start_Lat = GPS.Latitude
        start_Lon = GPS.Longitude
        end_Distance = parm1

    # Turn to a specified compass heading
    elif 'Turn To' == parm[0] :
        writeLog(LOG_DETAILS, 'Got Turn To of : ' + repr(parm[1]))
        Turning_To = True
        parm1 = int(parm[1])
        Turn_To_Angle = parm1
        if len(parm) > 2 :
            if parm[2] == 'left' :
                Arduino._serial_cmd(Arduino._Commands["steer"], -1*_degrees)
                Turn_To_Set = True
            elif parm[2] == 'right' :
                Arduino._serial_cmd(Arduino._Commands["steer"], _degrees)
                Turn_To_Set = True
        Auto_mode = False
        #execute('Moving Forward,10;')

    # Turn a number of degrees
    elif 'Turn Delta' == parm[0] :
        writeLog(LOG_DETAILS, 'Got Turn Delta of : ' + repr(parm[1]))
        parm1 = int(parm[1])
        Turning_Delta = True
        Turning_Delta_Init = True
        Turn_Delta_Angle = parm1
        Auto_mode = False
        #execute('Moving Forward,10;')
        
    # Stay on current compass heading for specified feet
    elif 'Follow Heading' == parm[0] :
        Heading_distance = parm[1]
        Following_Heading = True
        Auto_mode = False
        execute('Moving Forward,' + repr(Heading_distance) + ';')

#    elif 'Follow Course' in line :

#    elif 'Control Speed' in line :

    elif 'Delay' in line :
        parm1 = int(parm[1])
        Delaying = True
        delay_length = parm1
        delay_start = time.time()
        writeLog(LOG_DETAILS, 'Got Delay of :' + repr(delay_length))
    
