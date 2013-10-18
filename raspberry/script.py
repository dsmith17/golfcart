from log import *
import GPS
import Arduino
import Server
import commands

Script_File = [] 
Script_Running = False
command_num = 0

'''
start_script() takes a string as a paramater and parses it
into commands and starts the script running.
'''
def start_script(script) :
    global Script_Running
    global Script_File

    #Script_File = (script, 'r')
    Script_File = script.splitlines()
    writeLog(LOG_DETAILS, "New script file split: " + Script_File[0])
    Script_Running = True

'''
The Check() function is called by the contoller.py every
cycle. The Check() function returns if the script has not
been called. The Check() function checks if a script 
command is running, if not then executes the next command.
If the script was called and the commands are done executing
then Check() stops the script.
'''
def Check() :
    global Script_Running
    global Script_File
    global command_num

    # if the script command has not been called
    if not Script_Running :
        return

    # if the current script command is still running
    if commands.Command_Running :
        return

    # if there are still more commands to execute
    if command_num < len(Script_File) :
        command = Script_File[command_num]
        commands.Execute(command)
        command_num = 1 + command_num

    # if there are no more commands to execute
    elif len(Script_File) == command_num - 1 :
        command_num = 0
        Script_Running = False
        writeLog(LOG_DETAILS,"Ending script")
        return
