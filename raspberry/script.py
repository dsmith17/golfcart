from log import *
import GPS
import Arduino
import Server

Auto_mode = False
_Script = ''
_file = ''
MAX_FORWARD_FT = 999

def read(path) :
    global _Script

    try :
        _Script = open(path, 'r')
        Auto_mode = True            
    else :

def Check() :
    global _Script
    
    if Auto_mode :
        line in _Script.readlines()
        execute(line)

def execute(line) :
    parm = line.split(',')
    // Lets golfcart drift to a stop w/o brake
    if 'Soft Stop' in line :
        Arduino._serial_cmd(Arduino._Commands["speed"], 0)
        
    // Applies brake to stop
    elif 'Hard Stop' in line :
        Arduino._serial_cmd(Arduino._Commands["speed"], 0)
        Arduino._serial_cmd(Arduino._Commands["brake"], 1)
        
    // Go forward up to MAX_FORWARD_FT ft
    elif 'Move Forward' in line :

    // Turn to a specified compass heading
    elif 'Turn To' in line :

    // Turn a number of degrees
    elif 'Turn Delta' in line :

    elif 'Follow Heading' in line :

    elif 'Follow Course' in line :

    elif 'Control Speed' in line :

    elif 'Delay' in line :
    
