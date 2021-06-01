# -*- coding:utf-8 -*-

from time import sleep, strftime, time
import datetime
import os
import ADS1256
import RPi.GPIO as GPIO


filename = datetime.datetime.now()
with open(filename.strftime("%d-%m-%Y)+".csv","a") as file:
                            file.write("Time,Potentiometer,Photosensor\n")
        



# os.chdir("/home/pi/Data_Logging_Test") # test folder location for saving data 
# file = open("/home/pi/data_log_test.csv", "a")
# if os.stat("/home/pi/data_log_test.csv").st_size == 0:
#        file.write("Time,Potentiometer,Photosensor\n")
        
        
        

        
        
try:
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()

# when "while" used, no stoppping the recording of data, must be manually stopped
# when "used" used, make sure to include range() with the amount of data points requested. Currently recording only 100 data values
    #while True:
    for x in range(100):
        ADC_Value = ADC.ADS1256_GetAll()
        file.write(str(x)+","+str(datetime.datetime.now())+","+str(ADC_Value[0]*5.0/0x7fffff)+","+str(ADC_Value[1]*5.0/0x7fffff)+"\n")
        file.flush()
        sleep(0.1) # recording data every 0.1 seconds (or in other words 10 samples a second, 10 Hz) 
        print ("current time:-",datetime.datetime.now())
        print ("Potentiometer (0 ADC)= %lf"%(ADC_Value[0]*5.0/0x7fffff))
        print ("Photosensor Voltage (1 ADC)= %lf"%(ADC_Value[1]*5.0/0x7fffff))
    
except :
    GPIO.cleanup()
    print ("\r\nProgram end     ")
    exit()
   
