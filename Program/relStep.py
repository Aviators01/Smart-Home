"""
Timothy Queva
CS3130 Project
April 26, 2021

This code runs the relay switch and stepper motor
"""

from gpiozero import DigitalOutputDevice
from gpiozero import CompositeDevice
from gpiozero import GPIOPinMissing
from time import sleep


#Relay switch
class switch(DigitalOutputDevice):
    pass
    
#Door controls
class door():
    def __init__(self):
        self.__status = "UNKNOWN"
        self.__bolt = stepperControl(6,13,19,26)
        self.__bolt.setSpeed(50)
        
    def lock(self):
        self.__bolt.step(-95)
        self.__status = "LOCKED"
    
    def unlock(self):
        self.__bolt.step(95)
        self.__status = "UNLOCKED"
    
    def getStatus(self):
        return self.__status
    
    def close(self):
        self.__del__()
    
    def __del__(self):
        del self.__bolt

#Stepper motor
class stepperControl(CompositeDevice):
    def __init__(self,p1=None,p2=None,p3=None,p4=None,pin_factory=None):
        self.__case=0
        self.__speed=50
        
        if p1 == None or p2 == None or p3 == None or p4 == None:
            raise GPIOPinMissing("A pin has not been specified properly")
        
        super(stepperControl,self).__init__(
            out1 = DigitalOutputDevice(p1,pin_factory=pin_factory),
            out2 = DigitalOutputDevice(p2,pin_factory=pin_factory),
            out3 = DigitalOutputDevice(p3,pin_factory=pin_factory),
            out4 = DigitalOutputDevice(p4,pin_factory=pin_factory),
            _order =('out1','out2','out3','out4'),
            pin_factory = pin_factory)
        
    def setSpeed(self,speed):
        #reject everything except ints
        try:
            self.__speed = int(speed)
        except:
            raise ValueError("Only integers allowed for setSpeed()")
        
        #set min/max allowed speeds
        if self.__speed > 1023:
            self.__speed = 1023
        elif self.__speed < 0:
            self.__speed = 0
    
    def step(self,steps):
        #reject everything except ints
        try:
            int(steps)
        except:
            raise ValueError("Only integers allowed for step()")
        
        #Turn motor until target # of steps reached
        self.__case=0
        while 1:
            self.__case = 3-(steps % 4)
            
            if self.__case==0:
                self.out1.on()
                self.out2.off()
                self.out3.on()
                self.out4.off()
            elif self.__case==1:
                self.out1.off()
                self.out2.on()
                self.out3.on()
                self.out4.off()
            elif self.__case==2:
                self.out1.off()
                self.out2.on()
                self.out3.off()
                self.out4.on()
            elif self.__case==3:
                self.out1.on()
                self.out2.off()
                self.out3.off()
                self.out4.on()
            
            #Speed
            sleep(0.02)
            
            #Stops motors when target step count reached
            if steps > 0:
                steps -= 1
            elif steps < 0:
                steps += 1
            elif steps == 0:
                break
    
    #Releases motors for user to spin by hand if he so chooses
    def release(self):
        self.__case=0
        self.out1.off()
        self.out2.off()
        self.out3.off()
        self.out4.off()
    
    #Releases pins before destroying stepperControl object
    def __del__(self):
        self.out1.close()
        self.out2.close()
        self.out3.close()
        self.out4.close()

#For debugging purposes
if __name__ == '__main__':
    light = switch(2,active_high=False)
    light.on()
    sleep(3)
    light.off()
    light.close()
    
    test = stepperControl(6,13,19,26)
    test.setSpeed(50)
    test.step(95)
    test.release()
    del test