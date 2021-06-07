from datetime import datetime
import os
import time
from time import sleep
import ADS1256
import RPi.GPIO as GPIO

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from tkinter import *

window = Tk()
window.title("Helium Leak Detector")
window.geometry("400x300")

label0=Label(window,text='Input Test Information:', font=(14))
label0.grid(row=0,column=0,padx=5,pady=10)

label1=Label(window,text='Work Order:')
label1.grid(row=1,column=0,padx=5,pady=10)

label2=Label(window,text='Material #:')
label2.grid(row=2,column=0,padx=5,pady=10)

label3=Label(window,text='Serial #:')
label3.grid(row=3,column=0,padx=5,pady=10)

emptylabel = Label(window,text='',fg='green',font=(14))
emptylabel.grid(row=5,column=0)

data1=StringVar()
data2=StringVar()
data3=StringVar()


entry1 = Entry(window, textvariable=data1)
entry1.grid(row = 1,column = 1)

entry2 = Entry(window, textvariable=data2)
entry2.grid(row = 2,column = 1)

entry3 = Entry(window, textvariable=data3)
entry3.grid(row = 3,column = 1)

def submit_command():
    WorkOrder = data1.get()
    Material = data2.get()
    Serial = data3.get()
    emptylabel.config(text='SUBMITTED')
    print(WorkOrder)
    print(Material)
    print(Serial)
    return None

def clear_command():
    entry1.delete(0, END)
    entry2.delete(0, END)
    entry3.delete(0, END)
    emptylabel.config(text='')
    return None


submit_button = Button(window, text="Submit" , command=submit_command)
submit_button.grid(row=4,column=1)

clear_button = Button(window, text="Clear All" , command=clear_command)
clear_button.grid(row=5,column=1, pady = 10)

begin_button = Button(window, text="Begin Test" , command=window.destroy)
begin_button.grid(row=6,column=1,pady = 20)


window.mainloop()


# You can generate a Token from the "Tokens Tab" in the UI
token = "88G02Se715xyc9nQUuM4YdMyMVTsMHEJ4lzgkyVYF81YPlsCknKqNildzZWXpArDOQPRl_8cMao2sUIETBksTg=="
org = "saxire"
bucket = "dev_bucket"

client = InfluxDBClient(url="http://glin.saxire.net", token=token)


try:
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()
       
       while True:
        ADC_Value = ADC.ADS1256_GetAll()
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point("Helium Leak Test")\
          .tag("host", "jesse_greyshock")\
          .tag("Work Order","{}".format(data1.get()))\
          .tag("Material #","{}".format(data2.get()))\
          .tag("Serial #","{}".format(data3.get()))\
          .field("Potentiometer", ADC_Value[0]*5.0/0x7fffff)\
          .field("Photosensor", ADC_Value[1]*5.0/0x7fffff)\
          .time(datetime.utcnow(), WritePrecision.MS)
        write_api.write(bucket, org, point)
        print(ADC_Value[0]*5.0/0x7fffff)
        print(ADC_Value[1]*5.0/0x7fffff)
        print("\n")
        
except :
    GPIO.cleanup()
    print ("\r\nProgram end     ")
    exit()