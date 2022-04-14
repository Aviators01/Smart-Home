Timothy Queva
CS3130 Project
April 26, 2021


Description: These pairs of programs allows the user to monitor parts of his home. Code for monitoring and running
the MQ2 and MQ7 gas sensors has been implemented. The server program should send alerts to a logged in client when
minimum thresholds have been reached and when a relay switch has been tripped. This relay switch could be hooked up
to the oven, stove, furnace, or any combustion type appliance. On the other hand, the client is able to control a
stepper motor which can be imagined as being attached to a deadbolt thus allowing a neighbour, emergency personnel,
or any other applicable person to enter and check on the offending appliance.

-----------------------------------------------------------------------------------------------------------------------
Limitations:
	1. Both MQ2 and MQ7 sensors besides detecting carbon monoxide at differing ppm levels can be triggered by other
	   flammable gasses.
	2. It should also be noted that the MQ2 sensor is not very selective in terms of what it detects. In unofficial
	   tests, it was triggered by water vapour from the programmer's breath.

Potential vulnerabilities:
	1. MQ7 (carbon monoxide sensor) cycling is based on seconds as given by the unix epoch. Potential problem may
	   arise if time set before, on the epoch, or in the year 2038. This has not been tested yet.
------------------------------------------------------------------------------------------------------------------------

There are two parts to this sensor program. The client can run on any machine that has a python interpreter.
Alternatively, the client can be converted to a .exe windows program by a program found at py2exe.org (This hasn't been
tested though). The server portion however runs on a raspberry pi.


Instructions:
	1. Navigate to correct folder in raspberrypi terminal
	2. Start the server by typing: python3 SafeHome.py hostname -p 1123 -a server.pem -s mycert.crt
	3. On a different computer, access the server by typing: python3 Home.py <raspberry pi IP address> -p 1123 -a mycert.crt

-------------------------------------------------------------------------------------------------------------------------
Additional tips:
-for help, type: python3 SafeHome.py -h   <OR>    python3 Home.py -h
-To stop the server or client, type "exit" and hit ENTER