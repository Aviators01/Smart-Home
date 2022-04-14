"""
Timothy Queva
CS3130 Project
April 26, 2021


The server code that will control the hardware accessories connected to
the raspberry pi. Because GPIO is an element native to the raspberry pi,
this code cannot be run on anything other than a raspberry pi.
"""

import argparse, socket, ssl
import sys,select
from threading import Thread

import GasSensors
import relStep

'''
#For debugging tests on PC
from gpiozero import Device
from gpiozero.pins.mock import MockFactory
Device.pin_factory = MockFactory()
'''


def read():
    rfds,wfds,efds = select.select([sys.stdin],[],[],5)
    if rfds:
        return sys.stdin.readline()
    else:
        return ""

#sends message and adds end of message sequence of characters
def transmit(ssl_sock,msg):
    msg = msg + " \r\n*!*\r\n"
    msg = msg.encode('utf-8')
    ssl_sock.sendall(msg)
    
def recvall(sock,disableTOut = False):
    if disableTOut:
        sock.settimeout(None)
    else:
        sock.settimeout(2)
    
    data = b''
    while (data.decode('utf-8')).find(" \r\n*!*\r\n") == -1:
        try:
            more = sock.recv(1)
            data += more
        except socket.timeout:
            msg = "Request (" + data.decode('utf-8') + ") was not understood.\n\n"
            msg = msg.encode('utf-8')
            sock.sendall(msg)
            return ""
    data = data.decode('utf-8')
    data = data.strip(" \r\n*!*\r\n")
    return data

#sends help information to requester
def send_help(ssl_sock):
    reply = ("Available commands:\n" +
             "help              --displays this message\n" +
             "status: sensors   --shows gas sensor's measurements\n" +
             "status: switch    --shows switch status: on or off\n" +
             "status: door      --shows door status: locked or unlocked\n" +
             "door: lock        --rotates stepper motor to lock door\n" +
             "door: unlock      --rotates stepper motor to unlock door\n" +
             "switch: on        --turns relay switch on\n" +
             "switch: off       --turns relay switch off\n" +
             "exit              --closes client program.\n")
    transmit(ssl_sock,reply)

def server(host,port,pemfile,certfile=None):
    #Start threads to run MQ7 sensor and monitor it
    Thread(target=GasSensors.mq7Cycle, args="").start()
    Thread(target=GasSensors.monitorGasSensors, args="").start()
    
    #stores list of authorized chat users
    userlist = {}
    with open("AuthorizedUsers.txt") as v_users:
        for line in v_users:
            line.strip()
            line = line.split(":")
            userlist[line[0]] = line[1]
    
    #Creates objects to control components
    door = relStep.door()
    switch = relStep.switch(2,active_high=False)
    
    #Loads ssl stuff: certificate, private key, Certificate authority (cafile)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, cafile=certfile)
    context.load_cert_chain(pemfile)
    
    #create normal socket
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    #setup server socket
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((host, port))
    listener.listen(1)
    print('Listening at interface {!r} and port {}'.format(host, port))
    
    #Handles connections
    while 1:
        raw_sock, address = listener.accept()
        print('Connection from host {!r} and port {}'.format(*address))
        ssl_sock = context.wrap_socket(raw_sock, server_side=True)
        
        #Receives message from client
        msg = recvall(ssl_sock)
        
        #Process the message. If improper formatting, close socket.
        msg = msg.strip()
        try:
            user,command = msg.split(">:")
        except:
            ssl_sock.close()
            continue
        
        #May be redundant but just in case
        user = str(user)
        command = str(command)
        
        #Safely shutsdown server and releases GPIO pins
        data = read()   #non-blocking read
        if data.lower() == "exit\n":
            print()
            print("Shutting down the server now...\n")
            door.close()
            switch.close()
            print("Shutdown complete. Goodbye!")
            exit()
        
        #Check if user is authorized. If not, inform client, close socket.
        user = user.strip("<")
        user = user.strip(">")
        user = user.split(",")
        try:
            if userlist.get(user[0]) is None:
                transmit(ssl_sock,"revalidate")
                ssl_sock.close()
                continue
            if userlist[user[0]] != user[1]:
                transmit(ssl_sock,"revalidate")
                ssl_sock.close()
                continue
        except IndexError:
            transmit(ssl_sock,"revalidate")
            ssl_sock.close()
            continue
        
        #Process user's command
        command = command.strip()
        command = command.split(" ")
        
        
        '''
        "help              --displays this message\n" +
         "status: sensors   --shows gas sensor's measurements\n" +
         "status: switch    --shows switch status: on or off\n" +
         "status: door      --shows door status: locked or unlocked\n"+
         "door: lock        --rotates stepper motor to lock door\n" +
         "door: unlock      --rotates stepper motor to unlock door\n" +
         "switch: on        --turns relay switch on\n" +
         "switch: off       --turns relay switch off\n" +
         "exit              --closes client program.\n")
        '''
        
        #displays help information
        if command[0].lower()=="help":
            send_help(ssl_sock)
        
        #Displays statuses for sensors and switch
        elif command[0].lower()=="status:":
            command = str(command[1]).lower()
            command = command.strip()
            if command == "sensors":
                reply = ("MQ2 sensor reading is: " + GasSensors.readMQ2()+"\n"
                         "MQ7 sensor reading is: " + GasSensors.avgCO+"\n")
                transmit(ssl_sock,reply)
            elif command == "switch":
                if switch.value == 0:
                    reply = "Switch is: OFF"
                else: reply = "Switch is: ON"
                transmit(ssl_sock,reply)
            elif command == "door":
                reply = "Door lock status is: " + door.getStatus()
                transmit(ssl_sock,reply)
            else:
                reply = "Sorry! No such device exists!"
                transmit(ssl_sock,reply)
        
        #Executes user's door commands
        elif command[0].lower()=="door":
            command = str(command[1]).lower()
            command = command.strip()
            if command == "lock":
                door.lock()
            elif command == "unlock":
                door.unlock()
            else:
                reply = "Sorry! Your door command was not understood."
                transmit(ssl_sock,reply)
        
        #Executes user's switch commands
        elif command[0].lower()=="switch":
            command = str(command[1]).lower()
            command = command.strip()
            if command == "on":
                switch.on()
            elif command == "off":
                switch.off()
            else:
                reply = "Sorry! Your switch command was not understood"
                transmit(ssl_sock,reply)
        
        #Sends alert to user if MQ2 and MQ7 sensor readings too high
        elif command[0].lower() == "status?":
            #Sends Gas alert to client if necessary
            if GasSensors.alert == True:
                switch.off()
                reply = ("ALERT!\n" + 
                         "MQ2 gas sensor readings: "+GasSensors.readMQ2()+"\n"+
                         "MQ7 gas sensor readings: "+GasSensors.avgCO+"\n\n"+
                         "Relay switch has been turned: OFF")
            else: reply = ""
            transmit(ssl_sock,reply)
        
        else:
            reply = "Sorry. Your command was not understood."
            transmit(ssl_sock,reply)
        
        ssl_sock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server program that could '+
                                     'prevent your home from burning down.'+
                                     'Using this as a fail safe is not yet '+
                                     'recommended.')
    parser.add_argument('host', help='hostname or IP address')
    parser.add_argument('port', type=int, help='TCP port number')
    parser.add_argument('-a', metavar='cafile', default=None,
                        help='authority: path to CA certificate file')
    parser.add_argument('-s', metavar='certfile', default=None,
                        help='run as server: path to server PEM file')
    args = parser.parse_args()
    server(args.host, args.port, args.s, args.a)