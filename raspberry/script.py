from log import *
import GPS
import Arduino
import Server
import commands

Script_File = ''
Script_Running = False

def start_script(script) :
    Script_File = open(script, 'r')
    Script_Running = True

def Check() :
    if not Script_Running :
        return

    if commands.Command_Running :
        return

    command = Script_File.readline()
    if Script_File.eof() :
        Script_Running = False
        return

    commands.Execute(command)
    
