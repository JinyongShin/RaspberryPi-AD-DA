from datetime import datetime
import time
import ADS1256
import RPi.GPIO as GPIO

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from tkinter import *
import threading


switch = True
ADC = ADS1256.ADS1256()
ADC.ADS1256_init()

# You can generate a Token from the "Tokens Tab" in the UI
token = "88G02Se715xyc9nQUuM4YdMyMVTsMHEJ4lzgkyVYF81YPlsCknKqNildzZWXpArDOQPRl_8cMao2sUIETBksTg=="
org = "saxire"
bucket = "dev_bucket"

client = InfluxDBClient(url="http://glin.saxire.net", token=token)

window = Tk()
window.title("Helium Leak Detector")
window.geometry("500x300")

label0=Label(window,text='Input Test Information:', font=(18))
label0.grid(row=0,column=0,padx=5,pady=10)

labelname=Label(window,text='Operator PIN:')
labelname.grid(row=1,column=0,padx=5,pady=10)

label1=Label(window,text='Production Order:')
label1.grid(row=2,column=0,padx=5,pady=10)

label2=Label(window,text='Production Order Quantity:')
label2.grid(row=3,column=0,padx=5,pady=10)

label3=Label(window,text='Material #:')
label3.grid(row=4,column=0,padx=5,pady=10)

label4=Label(window,text='Serial # (if applicable):')
label4.grid(row=5,column=0,padx=5,pady=10)

emptylabel1 = Label(window,text='',fg='green',font=('bold',16))
emptylabel1.grid(row=6,column=2)

emptylabel2 = Label(window,text='',fg='blue',font=('bold',16))
emptylabel2.grid(row=0,column=1)

PINdata=StringVar()
data1=StringVar()
data2=StringVar()
data3=StringVar()
data4=StringVar()

entryPIN = Entry(window, textvariable=PINdata)
entryPIN.grid(row = 1,column = 1)

entry1 = Entry(window, textvariable=data1)
entry1.grid(row = 2,column = 1)

entry2 = Entry(window, textvariable=data2)
entry2.grid(row = 3,column = 1)

entry3 = Entry(window, textvariable=data3)
entry3.grid(row = 4,column = 1)

entry4 = Entry(window, textvariable=data4)
entry4.grid(row = 5,column = 1)

def submit_command():
    PIN = PINdata.get()
    WorkOrder = data1.get()
    Quantity = data2.get()
    Material = data3.get()
    Serial = data4.get()
    emptylabel1.config(text='SUBMITTED')
#     print(PIN)
#     print(WorkOrder)
#     print(Quantity)
#     print(Material)
#     print(Serial)
    return None

def clear_command():
    entry1.delete(0, END)
    entry2.delete(0, END)
    entry3.delete(0, END)
    entry4.delete(0, END)
    emptylabel1.config(text='')
    return None

def influxdb():
    def run():
        while (switch == True):
            ADC_Value = ADC.ADS1256_GetAll()
            write_api = client.write_api(write_options=SYNCHRONOUS)
            point = Point("Helium Leak Detector")\
                .tag("Operator", "{}".format(PINdata.get()))\
                .tag("Work Order","{}".format(data1.get()))\
                .tag("Work Order Quantity","{}".format(data2.get()))\
                .tag("Material #","{}".format(data3.get()))\
                .tag("Serial #","{}".format(data4.get()))\
                .field("Potentiometer", ADC_Value[0]*5.0/0x7fffff)\
                .field("Photosensor", ADC_Value[1]*5.0/0x7fffff)\
                .time(datetime.utcnow(), WritePrecision.MS)
            write_api.write(bucket, org, point)
            print(ADC_Value[0]*5.0/0x7fffff)
            print(ADC_Value[1]*5.0/0x7fffff)
            print("\n")
            if switch == False:
                break
    thread = threading.Thread(target=run)
    thread.start()
                       
def switch_on():
    global switch  
    switch = True  
    print ('Test Started')
    emptylabel2.config(text='TESTING...')
    influxdb()

def switch_off():  
    global switch  
    switch = False
    print ('Test Ended')
    emptylabel2.config(text='')

def kill():
 global switch  
 switch = False 
 window.destroy()


submit_button = Button(window, text="Submit" , command=submit_command)
submit_button.grid(row=2,column=2, padx=25)

clear_button = Button(window, text="Clear All" , command=clear_command)
clear_button.grid(row=3,column=2, pady = 5, padx=25)

begin_button = Button(window, text="Start Recording" , command=switch_on)
begin_button.grid(row=6,column=0,pady = 5)

end_button = Button(window, text="End Recording" , command=switch_off)
end_button.grid(row=6,column=1,pady = 5)

exit_button = Button(window, text="EXIT" , command=kill)
exit_button.grid(row=4,column=2,pady=5, padx=25)

window.mainloop()