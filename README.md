golfcart
========

Python, Arduino, and php code for a autonomous golf cart project

Version 1
=========

This projects goal is to create an autonomous golf cart controled through web applications. Physcial movment of the golf cart is done with motors controled with relays and motor-controlers. An Arudino mega board sends pwm signals to the motor-contorls based on commands recived from a raspberry-pi. This could be any computer with an internet contection. The raspberry-pi runs the python code client that requests commands from the web server the php script runs on. The php script writes a command to a file every time a user presses a button. The raspberry-pi communicates to over usb to the Arudino board sending the command recived from the web server. 

Python version 3.2 
Arduino version 1.1 (Arduino Mega boards rv. 1-3 tested)
