"""
Timothy Queva
CS3130 Project
April 26, 2021

This code runs and reads the gas sensors MQ2 and MQ7
"""

from gpiozero import MCP3008
from gpiozero import PWMOutputDevice
import time

#This runs the MQ7 sensor cycling between 5v and 1.5v
def mq7Cycle():
    global cleaningStatus
    global preheatingStatus
    cleaningStatus = False
    cleaning = False
    
    #Preheat sensor and wait till time is up
    preheatingStatus=True
    start = time.time()
    curr = time.time()
    COSensor = PWMOutputDevice(4,initial_value=1,frequency=1000000)
    while curr < start+120:
        curr = time.time()
        time.sleep(1)
    preheatingStatus=False
    
    #Cycle sensor between heating and detecting
    start = time.time()
    curr = start
    while 1:
        curr = int(time.time())
        
        #Turns sensor on fully to clean
        if cleaning==False and curr > start+60:
            #COMMAND: Turn on fully
            COSensor.value = 1
            
            cleaning = True
            cleaningStatus = cleaning
            start = curr = int(time.time())
        
        #PWM sensor in order to read
        elif cleaning==True and curr > start+90:
            #COMMAND: pulse width modulate
            COSensor.value = 0.3
            
            cleaning = False
            cleaningStatus = cleaning
            start = curr = int(time.time())
        
        #slows loop down
        time.sleep(1)

def readMQ2():
    sensor = MCP3008(0)
    return sensor.raw_value

def readMQ7():
    if cleaningStatus == False and preheatingStatus == False:
        sensor = MCP3008(1)
        return sensor.raw_value
    else: return -1


#This monitors both gas sensors for abnormal readings and issues alerts
def monitorGasSensors():
    global gGas
    global COGas
    global avgGas
    global avgCO
    global alert
    gGas = []
    COGas = []
    avgGas = 0
    avgCO = 0
    alert = False
    
    while 1:
        #Monitors MQ2 gas sensor
        gGas.insert(0,readMQ2())
        if len(gGas) > 30:
            gGas.pop()
            
            #calculates average gas measurment
            for measurement in gGas:
                avgGas += measurement
            avgGas = avgGas/30
                
        #Monitosr MQ7 gas sensor
        if readMQ7() != -1:
            COGas.insert(0,readMQ7())
            if len(COGas) > 30:
                COGas.pop()
            
            #calculates average gas measurment
            for measurement in COGas:
                avgCO += measurement
            avgCO = avgCO/30
        
        if avgGas > 500 and avgCO > 400:
            alert = True
        else: alert = False
        
        #slows loop down so read happens only once/second
        time.sleep(1)

'''
#For debugging purposes on PC-won't work due to no Mock pins for MCP3008
from gpiozero import Device
from gpiozero.pins.mock import MockFactory,MockPWMPin
Device.pin_factory = MockFactory(pin_class=MockPWMPin)
'''

#For debugging on a Raspberry Pi
if __name__ == '__main__':
    from threading import Thread
    
    Thread(target=mq7Cycle, args="").start()
    Thread(target=monitorGasSensors, args="").start()
    
    time.sleep(30)
    print("30s")
    time.sleep(30)
    print("1 min")
    time.sleep(30)
    print("1min 30s")
    time.sleep(30)
    print("Ready")
    
    print("MQ2 sensor reading: " + str(readMQ2()))
    time.sleep(30)
    print("Avg MQ7 sensor reading: " + str(avgCO))
    exit(1)