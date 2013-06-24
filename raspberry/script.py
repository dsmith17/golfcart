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
delta_Turning = 2
angle_Turning = 0


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
        _Script = file_buf
        Auto_mode = True
        execute_Command('steer mode', 0)

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
    
    if Auto_mode :
        line in _Script.readlines()
        if line != '' :
            execute(line)
        else :
            Auto_mode = False
            execute_Commmand('steer mode', 1)
    else :
        if Moving_Forward :
            if GPS.old_Latitude != GPS.Latitude or GPS.old_Longitude != GPS.Longitude :
                current_Distance = haversine(start_Lat, start_Lon, GPS.Latitude, GPS.Longitude)
                if current_Distance >= end_Distance - delta_Distance and current_Distance < end_Distance :
                    execute_Command("down", 0)
                elif current_Distance >= end_Distance :
                    execute_Command("stop", 0)
                    Moving_Forward = False
                    Auto_mode = True
#        if Turning_To :
            
#        if Turning_Delta :

def execute(line) :
    global start_Lat
    global start_Lon
    global end_Distance
    global Auto_mode
    global Moving_Forward
    global MAX_FORWARD_FT

    #Format line
    line = line.lstrip(';')    
    parm = line.split(',')
    
    # Lets golfcart drift to a stop w/o brake
    if 'Soft Stop' in line :
        Arduino._serial_cmd(Arduino._Commands["speed"], 0)
        
    # Applies brake to stop
    elif 'Hard Stop' in line :
        Arduino._serial_cmd(Arduino._Commands["speed"], 0)
        Arduino._serial_cmd(Arduino._Commands["brake"], 1)
        
    # Go forward up to MAX_FORWARD_FT ft
    elif 'Move Forward' in line :
        parm1 = int(parm[1])
        if parm1 > MAX_FORWARD_FT :
            parm1 = MAX_FORWARD_FT
        Moving_Forward = True
        execute_Command('up',0)
        execute_Command('up',0)
        Auto_mode = False
        start_Lat = GPS.Latitude
        start_Lon = GPS.Longitude
        end_Distance = parm1

    # Turn to a specified compass heading
    elif 'Turn To' in line :
        global Turning_To
        
        Turning_To = True
        
        
    # Turn a number of degrees
#    elif 'Turn Delta' in line :

#    elif 'Follow Heading' in line :

#    elif 'Follow Course' in line :

#    elif 'Control Speed' in line :

#    elif 'Delay' in line :
    
