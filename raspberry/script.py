from log import *
import GPS
import Arduino
import Server

Auto_mode = False
Moving_Forward = False
Instruction_num = 0
Command = [0,'',0] //index, instruction, paramater
_Script = ''
_file = ''
MAX_FORWARD_FT = 999

def execute_Command(instruct, parm) :
    global Command

    Command[0] = Instruction_num++
    Command[1] = instruct
    Command[2] = parm

    Arudino.Execute(Command)

def read(path) :
    global _Script
    global Command

    try :
        _Script = open(path, 'r')
        Auto_mode = True
        execute_Command('steer mode', 0)
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
        if parm[1] > MAX_FORWARD_FT :
            parm[1] = MAX_FORWARD_FT
        Moving_Forward = True
        execute_Command('up')

    // Turn to a specified compass heading
    elif 'Turn To' in line :

    // Turn a number of degrees
    elif 'Turn Delta' in line :

    elif 'Follow Heading' in line :

    elif 'Follow Course' in line :

    elif 'Control Speed' in line :

    elif 'Delay' in line :
    
