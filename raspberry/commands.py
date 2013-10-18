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
_last_direction = 0

Turn_Delta_Angle = 0
delta_angle_current = 0
_degrees = 100*(1000/360)
turn_active = False
Turn_To_Angle = 0
Turn_To_Direction = ''
have_direction = False

HEADING_DELTA = 3
heading_direction = 0
adjusting_heading = False

_Commands = { 'sstop', 'hstop', 'forward', 'turnto', 'turndelta', 'heading' }

def Execute(command) :
    global Command_Running, Current_Command, Command_Start
    global Delay_Time
    global Distance
    global Start_Lat, Start_Long
    global Turn_Delta_Angle, _degrees, turn_active
    global Turn_To_Angle, Turn_To_Direction
    global have_direction
    global heading_direction

    command = command.strip();
    command = command.rstrip(';')
    parm = command.split(',')
    writeLog(LOG_NEW_COMMAND, parm)

    if not parm[0] in _Commands :
        writeLog(LOG_ERROR, "Unknown Command... Skipping");
        return
    
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
    #A turnto command can not be called as the first command or after a delay
    #as the GPS.Direction has to be set before the commands execute stage.
    elif parm[0] == 'turnto' : #format "turnto,compass_heading,turning_left_or_right;"
        try :
            if GPS.Direction == GPS.invalid_Direction :
                writeLog(LOG_ERROR, "Command turnto failed... must have a valid direction")
                Command_Running = False
                return
            Turn_To_Angle = int(parm[1])
            if parm[2] == 'right' :
                writeLog(LOG_DETAILS, "Turning Right")
                Arduino._serial_cmd(Arduino._Commands["steer"], _degrees)
            elif parm[2] == 'left' :
                writeLog(LOG_DETAILS, "Turning Left")
                Arduino._serial_cmd(Arduino._Commands["steer"], -_degrees)
            else :
                writeLog(LOG_ERROR, "Unknown turnto Direction... Skipping");
                Turn_To_Angle = 0
                Command_Running = False
                return
            if Arduino.Speed == 0 :
                Arduino._serial_cmd(Arduino._Commands["speed"], 1700)
                turn_active = True
            if GPS.Direction != 0 :
                have_direction = True
            Turn_To_Direction = parm[2]            
        except ValueError :
            Turn_To_Angle = 0
            Command_Running = False
            writeLog(LOG_ERROR, "Command turnto failed... Conversion fail");
    #A turndelta command can not be called as the first command or after a delay
    #as the GPS.Direction has to be set before the commands execute stage.
    #Formats turndelta parmaters into a turnto call and calls execute again
    elif parm[0] == 'turndelta' :
        try :
            if GPS.Direction == GPS.invalid_Direction :
                writeLog(LOG_ERROR, "Command turndelta failed... must have a valid direction")
                Command_Running = False
                return
            turn_direction = ''
            Turn_Delta_Angle = int(parm[1])
            delta_heading = GPS.Direction + Turn_Delta_Angle
            delta_heading = int(delta_heading)
            if delta_heading < 0 :
                delta_heading = 360 + delta_heading
            if delta_heading > 360 :
                delta_heading = delta_heading - 360
            if Turn_Delta_Angle > 0 :
                turn_direction = 'right'
            elif Turn_Delta_Angle < 0 :
                turn_direction = 'left'
            Execute('turnto,'+str(delta_heading)+','+turn_direction+';')           
        except ValueError :
            Turn_Delta_Angle = 0
            Command_Running = False
            writeLog(LOG_ERROR, "Command turndelta failed... Conversion fail");
    elif parm[0] == 'forward' :
        try :
            Distance = int(parm[1])
            Start_Lat = GPS.Latitude
            Start_Long = GPS.Longitude
            Arduino._serial_cmd(Arduino._Commands["speed"], 1700) #starts the golf cart moving
        except ValueError :
            Distance = 0
            Command_Running = False
            logWrite(LOG_ERROR, "Command forward failed... Conversion fail");
    elif parm[0] == 'heading' :
        try :
            Distance = int(parm[1])
            if GPS.Direction != GPS.invalid_Direction :
                have_direction = True
                heading_direction = GPS.Direction
            Start_Lat = GPS.Latitude
            Start_Long = GPS.Longitude
            Arduino._serial_cmd(Arduino._Commands["speed"], 1700) #starts the golf cart moving
        except ValueError :
            Distance = 0
            Command_Running = False
            logWrite(LOG_ERROR, "Command heading failed... Conversion fail")
    elif parm[0] == 'course' :
        try :
            Distance = int(parm[1])
            heading_direction = int(parm[2])
            if heading_direction > 360 or heading_direction < 0 :
                logWrite(LOG_ERROR, "Command course failed... direction not between 0 and 360")
                return
            Start_Lat = GPS.Latitude
            Start_Long = GPS.Lonitude
            Arduino._serial_cmd(Arduino._Commands["speed"], 1700) #starts the golf cart moving
        except ValueError :
            Distance = 0
            Command_Running = False
            logWrite(LOG_ERROR, "Command course failed... Conversion fail")
    elif parm[0] == 'delay' :
        Delay_Time = int(parm[1])
    else :
        writeLog(LOG_ERROR, 'Unrecognized command')
        Command_Running = False

def Check() :
    global Distance
    global Command_Running, Current_Command, Command_Start
    global Delay_Time
    global Turn_Delta_Angle, delta_angle_current, turn_active
    global Turn_To_Angle, Turn_To_Direction, have_direction
    global HEADING_DELTA, heading_direction, adjusting_heading

    if not Command_Running :
        return

    if Current_Command == 'sstop' :
        if GPS.Connected and GPS.Speed == 0.0 :
            Command_Running = False
            Arduino._serial_cmd(Arduino._Commands["brake"], 0) # releases the brake
        if Command_Start + Delay_Time < time.time() :
            Command_Running = False
            Arduino._serial_cmd(Arduino._Commands["brake"], 0) # releases the brake
    elif Current_Command == 'hstop' :
        # I don't know if I have the correct brake status here
        if GPS.Connected and GPS.Speed == 0.0 and Arduino.Brake == 3:
            Command_Running = False
            Arduino._serial_cmd(Arduino._Commands["brake"], 0) # releases the brake
        if Command_Start + Delay_Time < time.time() :
            Command_Running = False
            Arduino._serial_cmd(Arduino._Commands["brake"], 0) # releases the brake
    elif Current_Command == 'turnto' :
        cur_dir = GPS.Direction
        if have_direction == True :
            if Turn_To_Angle - HEADING_DELTA < cur_dir and cur_dir < Turn_To_Angle + HEADING_DELTA :
                Arduino._serial_cmd(Arduino._Commands["steer"], 0)
                if turn_active :
                    Arduino._serial_cmd(Arduino._Commands["speed"], 0)
                    turn_active = False
                Command_Running = False
        else :
            if GPS.Direction != GPS.invalid_Direction :
                have_direction = True
    elif Current_Command == 'forward' :
        distance = GPS.haversine(Start_Lat, Start_Long, GPS.Latitude, GPS.Longitude)
        if distance > Distance :
            Command_Running = False
            Arduino._serial_cmd(Arduino._Commands["speed"], 0)
    elif Current_Command == 'heading' :
        if not have_direction :
            if GPS.Direction != GPS.invalid_Direction :
                have_direction = True
                heading_direction = GPS.Direction
            else :
                return 
        distance = GPS.haversine(Start_Lat, Start_Long, GPS.Latitude, GPS.Longitude)
        cur_dir = GPS.Direction
        if distance > Distance :
            Command_Running = False
            Arduino._serial_cmd(Arduino._Commands["speed"], 0)
            Arduino._serial_cmd(Arduino._Commands["steer"], 0)
        if cur_dir - heading_direction > HEADING_DELTA and not adjusting_heading : # veering right
            Arduino._serial_cmd(Arduino._Commands["steer"], -_degrees)
            adjusting_heading = True
        elif -cur_dir + heading_direction > HEADING_DELTA and not adjusting_heading: # veering left
            Arduino._serial_cmd(Arduino._Commands["steer"], _degrees)
            adjusting_heading = True
        # assumes check() is often enough to stop turn before veering opposite way
        elif -cur_dir + heading_direction < HEADING_DELTA and cur_dir - heading_direction < HEADING_DELTA : 
            Arduino._serial_cmd(Arduino._Commands["steer"], 0)
            adjusting_heading = False
    elif Current_Command == 'course' :
        distance = GPS.haversine(Start_Lat, Start_Long, GPS.Latitude, GPS.Longitude)
        cur_dir = GPS.Direction
        if distance > Distance :
            Command_Running = False
            Arduino._serial_cmd(Arduino._Commands["speed"], 0)
            Arduino._serial_cmd(Arudino._Commands["steer"], 0)
        if cur_dir - heading_direction > HEADING_DELTA and not adjusting_heading : # veering right or need to turn left
            Arduino._serial_cmd(Arudino._Commands["steer"], -_degrees)
            adjusting_heading = True
        elif -cur_dir + heading_direction > HEADING_DELTA and not adjusting_heading: # veering left or need to turn right
            Arduino._serial_cmd(Arudino._Commands["steer"], _degrees)
            adjusting_heading = True
        elif -cur_dir + heading_direction < HEADING_DELTA and cur_dir - heading_direction < HEADING_DELTA : # assumes check() is often enough to stop turn before veering opposite way
            Arduino._serial_cmd(Arudino._Commands["steer"], 0)
            adjusting_heading = False
    elif Current_Command == 'delay' :
        if Command_Start + Delay_Time < time.time() :
            Command_Running = False
    else :
        writeLog(LOG_ERROR, 'Unrecognized command')
        Command_Running = False
