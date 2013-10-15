from log import *
import GPS
import Arduino
import Server
import commands

Script_File = ''
Script_Running = False

def start_script(script) :
    global Script_Running
    global Script_File

    #Script_File = (script, 'r')
    Script_File = script
    Script_Running = True

def Check() :
    global Script_Running
    global Script_File

    if not Script_Running :
        return

    if commands.Command_Running :
        return

    command = Script_File.readline()
    if Script_File.eof() :
        Script_Running = False
        return

    commands.Execute(command)
    
