"""
Timothy Queva
CS3130 Project
April 26, 2021

This program allows one to contact the SafeHome.py program running on
a raspberry pi.
"""

import argparse, socket, ssl
import sys,select
import time

#sends message and adds end of message sequence of characters
def transmit(ssl_sock,msg):
    msg = msg + " \r\n*!*\r\n"
    msg = msg.encode('utf-8')
    ssl_sock.sendall(msg)

#receives messages from server
def receive(sock,host,port):
    sock.settimeout(2)
    data = b''
    while (data.decode('utf-8',errors='ignore')).find(" \r\n*!*\r\n") == -1:
        try:
            more = sock.recv(1)
            data += more
        except socket.timeout:
            print("Incomplete response received.")
            print("Here is what we've received so far:")
            data = data.decode('utf-8')
            return data
        except ConnectionRefusedError:
            print()
            print("Sorry, the command/message was refused.")
            print("There doesn't appear to be a server " +
                  "at that interface (" + str(host) +
                  ", " + str(port) + ").")
            exit()
    data = data.decode('utf-8')
    data = data.strip(" \r\n*!*\r\n")
    return data

def read():
    rfds,wfds,efds = select.select([sys.stdin],[],[],5)
    if rfds:
        return sys.stdin.readline()
    else:
        return ""

def createSslSocket(host,port,certfile=None):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                         cafile=certfile)
    
    #create socket and connect to server
    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_sock.connect((host, port))
    
    #Wrap the socket
    ssl_sock = context.wrap_socket(raw_sock, server_hostname=host)
    
    return ssl_sock

def client(host,port,certfile):
    print("Welcome to safe home client program")
    print()
    print("Please note that if program advances to next line " +
          "while you are still typing,\n" +
          "your whole message will still be sent.\n")
    
    username = input("Please enter your username: ")
    username = username.strip()
    password = input("Please enter your password: ")
    password = password.strip()
    
    #Interface
    startT = time.time()
    currT = startT
    while True:
        print()
        sys.stdout.write("-->: ")
        sys.stdout.flush()
        data = read()   #non-blocking read
        
        #allows user to exit program without reliance on ctrl + c
        if data.lower() == "exit\n":
            print()
            print("Thank you for using SafeHome client. Goodbye!")
            exit()
        
        #sends msg to server if user hits ENTER key
        if data.find("\n") != -1:
            data = data.strip()
            ssl_sock = createSslSocket(host, port, certfile)
            data = "<" + str(username) + "," + str(password) + ">: " + data
            transmit(ssl_sock,data)
            
            #Receive, print, and close socket
            data = receive(ssl_sock,host,port)
            if data == "revalidate":
                print("Username and/or password not recognized.")
                username = input("Please enter your username: ")
                username = username.strip()
                password = input("Please enter your password: ")
                password = password.strip()
            else: print(data)
            ssl_sock.close()
        
        #Get status update automatically every minute
        currT = time.time()
        if currT > startT+60:
            msg = "<" + str(username) + "," + str(password) + ">: " + "status?"
            ssl_sock = createSslSocket(host, port, certfile)
            transmit(ssl_sock,msg)
            msg = receive(ssl_sock,host,port)
            
            #Alerts user if relay tripped or gas concentration above normal
            if "ALERT!" in msg:
                msg = str(msg[6:])
                msg = msg.strip()
                print(msg)
            ssl_sock.close()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client program to contact '+
                                     'safe home server program running on a '+
                                     'raspberry pi.\nType \"help\" to see '+
                                     'available commands.')
    parser.add_argument('host', help='hostname or IP address')
    parser.add_argument('port', type=int, help='TCP port number')
    parser.add_argument('-a', metavar='cafile', default=None,
                        help='authority: path to CA certificate file')
    args = parser.parse_args()
    client(args.host, args.port, args.a)