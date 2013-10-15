from log import *
import GPS
import Arduino
import Server
import commands

Script_File = [] 
Script_Running = False
command_num = 0

def start_script(script) :
    global Script_Running
    global Script_File

    #Script_File = (script, 'r')
    Script_File = script.splitlines()
    Script_Running = True

def Check() :
    global Script_Running
    global Script_File
    global command_num

    if not Script_Running :
        return

    if commands.Command_Running :
        return

    command = Script_File[command_num]
    command_num += 1
    if len(Script_File) <= command_num :
        command_num = 0
        Script_Running = False
        return

    commands.Execute(command)
    
