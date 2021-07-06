import os
import time
from time import sleep
from datetime import datetime
import ADS1256
import RPi.GPIO as GPIO

os.chdir("/home/pi/Data_Logging_Test")
date = datetime.now().strftime("%d-%B-%Y_%H-%M-%S")
file = open(date+".csv", "a")
if os.stat(date+".csv").st_size == 0:
        file.write("Time,Potentiometer,Photosensor\n")



try:
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()
    
    for x in range(100):
        ADC_Value = ADC.ADS1256_GetAll()
        now = datetime.now()
        file.write(str(now)+","+str(ADC_Value[0]*5.0/0x7fffff)+","+str(ADC_Value[1]*5.0/0x7fffff)+"\n")
        file.flush()
        time.sleep(0.1)
        
except :
    GPIO.cleanup()
    print ("\r\nProgram end     ")
    exit()
