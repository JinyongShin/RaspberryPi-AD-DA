import os
import csv
import time
from time import sleep
from datetime import datetime
import ADS1256
import RPi.GPIO as GPIO
from scipy.interpolate import interp1d
from tkinter import *
import threading
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

os.chdir("/home/pi/Data_Logging_Test")
date = datetime.now().strftime("%d-%B-%Y_%H-%M-%S")
filename = date+".csv"
# if os.stat(date+".csv").st_size == 0:
#         file.write("Time,Operator,Leak Rate\n")
        
# You can generate a Token from the "Tokens Tab" in the UI
token = "88G02Se715xyc9nQUuM4YdMyMVTsMHEJ4lzgkyVYF81YPlsCknKqNildzZWXpArDOQPRl_8cMao2sUIETBksTg=="
org = "saxire"
bucket = "dev_bucket" # change to write to different bucket

client = InfluxDBClient(url="http://glin.saxire.net", token=token)

x = [0,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.00,1.05,1.10,1.15,1.20,1.25,1.30,1.35,1.40,1.45,1.50,1.55,1.60,1.65,1.70,1.75,1.80,1.85,1.90,1.95,2.00,2.05,2.10,2.15,2.20,2.25,2.30,2.35,2.40,2.45,2.50,2.55,2.60,2.65,2.70,2.75,2.80,2.85,2.90,2.95,3.00,3.05,3.10,3.15,3.20,3.25,3.30,3.35,3.40,3.45,3.50,3.55,3.60,3.65,3.70,3.75,3.80,3.85,3.90,3.95,4.00,4.05,4.10,4.15,4.20,4.25,4.30,4.35,4.40,4.45,4.50,4.55,4.60,4.65,4.70,4.75,4.80,4.85,4.90,4.95,5.00,5.10,5.20,5.30,5.40,5.50,5.60,5.70,5.80,5.90,6.00,6.10,6.20,6.30,6.40,6.50,6.60,6.70,6.80,6.90,7.00,7.10,7.20,7.30,7.40,7.50,7.60,7.70,7.80,7.90,8.00]
y = [0,3.07E-12,1.12E-11,2.08E-11,3.20E-11,4.51E-11,6.03E-11,7.80E-11,9.84E-11,1.22E-10,1.49E-10,1.80E-10,2.16E-10,2.57E-10,3.04E-10,3.57E-10,4.18E-10,4.88E-10,5.67E-10,6.56E-10,7.58E-10,8.74E-10,1.00E-09,1.15E-09,1.32E-09,1.51E-09,1.73E-09,1.97E-09,2.25E-09,2.56E-09,2.91E-09,3.30E-09,3.75E-09,4.25E-09,4.82E-09,5.46E-09,6.18E-09,6.99E-09,7.91E-09,8.93E-09,1.01E-08,1.14E-08,1.29E-08,1.45E-08,1.64E-08,1.85E-08,2.08E-08,2.35E-08,2.64E-08,2.98E-08,3.35E-08,3.77E-08,4.25E-08,4.78E-08,5.38E-08,6.05E-08,6.81E-08,7.66E-08,8.61E-08,9.68E-08,1.09E-07,1.22E-07,1.38E-07,1.55E-07,1.74E-07,1.95E-07,2.19E-07,2.46E-07,2.77E-07,3.11E-07,3.49E-07,3.92E-07,4.40E-07,4.95E-07,5.55E-07,6.24E-07,7.00E-07,7.86E-07,8.83E-07,9.91E-07,1.11E-06,1.25E-06,1.40E-06,1.57E-06,1.77E-06,1.98E-06,2.23E-06,2.50E-06,2.81E-06,3.15E-06,3.53E-06,3.97E-06,4.45E-06,5.00E-06,5.61E-06,6.29E-06,7.06E-06,7.93E-06,8.89E-06,9.98E-06,1.26E-05,1.58E-05,1.99E-05,2.51E-05,3.16E-05,3.98E-05,5.01E-05,6.31E-05,7.94E-05,1.00E-04,1.26E-04,1.58E-04,2.00E-04,2.51E-04,3.16E-04,3.98E-04,5.01E-04,6.31E-04,7.94E-04,1.00E-03,1.26E-03,1.58E-03,2.00E-03,2.51E-03,3.16E-03,3.98E-03,5.01E-03,6.31E-03,7.94E-03,1.00E-02]
z = [0,3.07E-10,1.12E-09,2.08E-09,3.20E-09,4.51E-09,6.03E-09,7.80E-09,9.84E-09,1.22E-08,1.49E-08,1.80E-08,2.16E-08,2.57E-08,3.04E-08,3.57E-08,4.18E-08,4.88E-08,5.67E-08,6.56E-08,7.58E-08,8.74E-08,1.00E-07,1.15E-07,1.32E-07,1.51E-07,1.73E-07,1.97E-07,2.25E-07,2.56E-07,2.91E-07,3.30E-07,3.75E-07,4.25E-07,4.82E-07,5.46E-07,6.18E-07,6.99E-07,7.91E-07,8.93E-07,1.01E-06,1.14E-06,1.29E-06,1.45E-06,1.64E-06,1.85E-06,2.08E-06,2.35E-06,2.64E-06,2.98E-06,3.35E-06,3.77E-06,4.25E-06,4.78E-06,5.38E-06,6.05E-06,6.81E-06,7.66E-06,8.61E-06,9.68E-06,1.09E-05,1.22E-05,1.38E-05,1.55E-05,1.74E-05,1.95E-05,2.19E-05,2.46E-05,2.77E-05,3.11E-05,3.49E-05,3.92E-05,4.40E-05,4.95E-05,5.55E-05,6.24E-05,7.00E-05,7.86E-05,8.83E-05,9.91E-05,1.11E-04,1.25E-04,1.40E-04,1.57E-04,1.77E-04,1.98E-04,2.23E-04,2.50E-04,2.81E-04,3.15E-04,3.53E-04,3.97E-04,4.45E-04,5.00E-04,5.61E-04,6.29E-04,7.06E-04,7.93E-04,8.89E-04,9.98E-04,1.26E-03,1.58E-03,1.99E-03,2.51E-03,3.16E-03,3.98E-03,5.01E-03,6.31E-03,7.94E-03,1.00E-02,1.26E-02,1.58E-02,2.00E-02,2.51E-02,3.16E-02,3.98E-02,5.01E-02,6.31E-02,7.94E-02,1.00E-01,1.26E-01,1.58E-01,2.00E-01,2.51E-01,3.16E-01,3.98E-01,5.01E-01,6.31E-01,7.94E-01,1.00E+00]


FL = interp1d(x, y, kind = 'linear')
GL = interp1d(x, z, kind = 'linear')

window = Tk()

OP=StringVar()
entry1 = Entry(window, textvariable=OP)
entry1.grid(row = 1,column = 1,ipadx=30,ipady=5)
entry1.focus_set()

ADC = ADS1256.ADS1256()
ADC.ADS1256_init()

switch = True


def switch_on():
    global switch  
    switch = True  
    print ('Test Started')
    testing()
    
def switch_off():
    global switch  
    switch = False
    print ('Test Ended')

def testing():
    def run():
        with open(filename,'w',newline='') as log:
            while (switch == True):
                ADC_Value = ADC.ADS1256_GetAll()
                R1 = 4703
                R2 = 2192
                Vout2 = ADC_Value[2]*5.0/0x7fffff
                Vs2 = ((Vout2)*((R1+R2)/(R2)))
                interpFLVs2 = FL(Vs2)
                FLVs2 = interpFLVs2*(1.0)

                now = datetime.utcnow()
            
                log.write("{0},{1}\n".format(now,FLVs2))
                
                print('Leak Rate =',FLVs2)
                print('Time =',now.strftime('%H:%M:%S.%f'))
                print(filename)
                print ("\33[9A")
                
            if switch == False:
                write_api = client.write_api(write_options=SYNCHRONOUS)
    
                def read_data():
                    with open(filename) as f:
                        return [x.split(',') for x in f.readlines()[1:]]

                    a = read_data()

                    for metric in a:
                        influx_metric = [{
                            "measurement": "Test2CSV",
                            "time": a[0],
                            "tags": {
                                "Operator": OP.get()
                                },
                            "fields": {
                                 "value": a[1]
                            }
                        }]
                        write_api.write(bucket,org,influx_metric)
                        break
    thread = threading.Thread(target=run)
    thread.start()        
        
begin_button = Button(window, text="Start Recording" ,font=('bold',20),fg='white', bg='firebrick4',command=switch_on)
begin_button.grid(row=2,column=1,pady=25,padx=15,ipady=20)

end_button = Button(window, text="End Recording" ,font=('bold',20),fg='white', bg='firebrick4',command=switch_off)
end_button.grid(row=3,column=1,pady=25, padx=15,ipady=20)

window.mainloop()