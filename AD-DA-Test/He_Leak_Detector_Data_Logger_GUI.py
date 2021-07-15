#!/usr/bin/env python3

from datetime import datetime
import time
import ADS1256
import os
import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from tkinter import *
import threading
import mysql.connector
from scipy.interpolate import interp1d
import RPi.GPIO as GPIO
import sys


# global switch initialize
switch = True

# connect to ADC HAT on Raspberry Pi
ADC = ADS1256.ADS1256()
ADC.ADS1256_init()

# folder to store CSV data
os.chdir("/home/pi/Data_Logging")

# You can generate a Token from the "Tokens Tab" in the UI
token = "88G02Se715xyc9nQUuM4YdMyMVTsMHEJ4lzgkyVYF81YPlsCknKqNildzZWXpArDOQPRl_8cMao2sUIETBksTg=="
org = "saxire"
bucket = "dev_bucket" # change to write to different bucket

client = InfluxDBClient(url="http://glin.saxire.net", token=token)

# Voltage and Leak Rate conversion data pulled from Detector manual
Volts = [0,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.00,1.05,1.10,1.15,1.20,1.25,1.30,1.35,1.40,1.45,1.50,1.55,1.60,1.65,1.70,1.75,1.80,1.85,1.90,1.95,2.00,2.05,2.10,2.15,2.20,2.25,2.30,2.35,2.40,2.45,2.50,2.55,2.60,2.65,2.70,2.75,2.80,2.85,2.90,2.95,3.00,3.05,3.10,3.15,3.20,3.25,3.30,3.35,3.40,3.45,3.50,3.55,3.60,3.65,3.70,3.75,3.80,3.85,3.90,3.95,4.00,4.05,4.10,4.15,4.20,4.25,4.30,4.35,4.40,4.45,4.50,4.55,4.60,4.65,4.70,4.75,4.80,4.85,4.90,4.95,5.00,5.10,5.20,5.30,5.40,5.50,5.60,5.70,5.80,5.90,6.00,6.10,6.20,6.30,6.40,6.50,6.60,6.70,6.80,6.90,7.00,7.10,7.20,7.30,7.40,7.50,7.60,7.70,7.80,7.90,8.00]
Signal_He_FL = [0,3.07E-12,1.12E-11,2.08E-11,3.20E-11,4.51E-11,6.03E-11,7.80E-11,9.84E-11,1.22E-10,1.49E-10,1.80E-10,2.16E-10,2.57E-10,3.04E-10,3.57E-10,4.18E-10,4.88E-10,5.67E-10,6.56E-10,7.58E-10,8.74E-10,1.00E-09,1.15E-09,1.32E-09,1.51E-09,1.73E-09,1.97E-09,2.25E-09,2.56E-09,2.91E-09,3.30E-09,3.75E-09,4.25E-09,4.82E-09,5.46E-09,6.18E-09,6.99E-09,7.91E-09,8.93E-09,1.01E-08,1.14E-08,1.29E-08,1.45E-08,1.64E-08,1.85E-08,2.08E-08,2.35E-08,2.64E-08,2.98E-08,3.35E-08,3.77E-08,4.25E-08,4.78E-08,5.38E-08,6.05E-08,6.81E-08,7.66E-08,8.61E-08,9.68E-08,1.09E-07,1.22E-07,1.38E-07,1.55E-07,1.74E-07,1.95E-07,2.19E-07,2.46E-07,2.77E-07,3.11E-07,3.49E-07,3.92E-07,4.40E-07,4.95E-07,5.55E-07,6.24E-07,7.00E-07,7.86E-07,8.83E-07,9.91E-07,1.11E-06,1.25E-06,1.40E-06,1.57E-06,1.77E-06,1.98E-06,2.23E-06,2.50E-06,2.81E-06,3.15E-06,3.53E-06,3.97E-06,4.45E-06,5.00E-06,5.61E-06,6.29E-06,7.06E-06,7.93E-06,8.89E-06,9.98E-06,1.26E-05,1.58E-05,1.99E-05,2.51E-05,3.16E-05,3.98E-05,5.01E-05,6.31E-05,7.94E-05,1.00E-04,1.26E-04,1.58E-04,2.00E-04,2.51E-04,3.16E-04,3.98E-04,5.01E-04,6.31E-04,7.94E-04,1.00E-03,1.26E-03,1.58E-03,2.00E-03,2.51E-03,3.16E-03,3.98E-03,5.01E-03,6.31E-03,7.94E-03,1.00E-02]
Signal_He_GL = [0,3.07E-10,1.12E-09,2.08E-09,3.20E-09,4.51E-09,6.03E-09,7.80E-09,9.84E-09,1.22E-08,1.49E-08,1.80E-08,2.16E-08,2.57E-08,3.04E-08,3.57E-08,4.18E-08,4.88E-08,5.67E-08,6.56E-08,7.58E-08,8.74E-08,1.00E-07,1.15E-07,1.32E-07,1.51E-07,1.73E-07,1.97E-07,2.25E-07,2.56E-07,2.91E-07,3.30E-07,3.75E-07,4.25E-07,4.82E-07,5.46E-07,6.18E-07,6.99E-07,7.91E-07,8.93E-07,1.01E-06,1.14E-06,1.29E-06,1.45E-06,1.64E-06,1.85E-06,2.08E-06,2.35E-06,2.64E-06,2.98E-06,3.35E-06,3.77E-06,4.25E-06,4.78E-06,5.38E-06,6.05E-06,6.81E-06,7.66E-06,8.61E-06,9.68E-06,1.09E-05,1.22E-05,1.38E-05,1.55E-05,1.74E-05,1.95E-05,2.19E-05,2.46E-05,2.77E-05,3.11E-05,3.49E-05,3.92E-05,4.40E-05,4.95E-05,5.55E-05,6.24E-05,7.00E-05,7.86E-05,8.83E-05,9.91E-05,1.11E-04,1.25E-04,1.40E-04,1.57E-04,1.77E-04,1.98E-04,2.23E-04,2.50E-04,2.81E-04,3.15E-04,3.53E-04,3.97E-04,4.45E-04,5.00E-04,5.61E-04,6.29E-04,7.06E-04,7.93E-04,8.89E-04,9.98E-04,1.26E-03,1.58E-03,1.99E-03,2.51E-03,3.16E-03,3.98E-03,5.01E-03,6.31E-03,7.94E-03,1.00E-02,1.26E-02,1.58E-02,2.00E-02,2.51E-02,3.16E-02,3.98E-02,5.01E-02,6.31E-02,7.94E-02,1.00E-01,1.26E-01,1.58E-01,2.00E-01,2.51E-01,3.16E-01,3.98E-01,5.01E-01,6.31E-01,7.94E-01,1.00E+00]

FL = interp1d(Volts, Signal_He_FL) # Fine Leak (main)
GL = interp1d(Volts, Signal_He_GL) # Gross Leak

# estimated/recorded values to determine the conversion of voltage to inlet pressure
Volts2 = [0,2.45,7.07,10]
Inlet_Pressure = [0,1.0E-3,2.0E2,1E3]

IP = interp1d(Volts2, Inlet_Pressure)

# PIN window
def code(value):

    global pin
    global UserPIN, UserName

    def default_label():
        error_label.config(text='')
        return
        
    # back button
    if value == '*':
        pin = pin[:-1]
        e.delete('0', 'end')
        e.insert('end', pin)
    
    # done button
    elif value == '#':
        
        # access SQL database for Operator PINs
        serverIP='10.10.9.107'
        # sqlDatabase = 'allusers'
        # sqlTable = 'users'
        sqlUsername ='jgreyshock'
        sqlPassword = 'Welcome21!'

        cnx = mysql.connector.connect(user=sqlUsername, password=sqlPassword, host=serverIP)
        cursor = cnx.cursor()

        selectString = 'select UserPIN, UserName from allusers.users where UserPIN={}'.format(pin)
        cursor.execute(selectString)
        Result = cursor.fetchall()
        
        for UserPIN, UserName in Result:
            openwindow() 
        else:
            pin = ''
            e.delete('0', 'end')
            error_label.config(text='PIN ERROR!')
            root.after(1500, default_label)
          
    else:
        pin += value
        e.insert('end', value)

keys = [
    ['1', '2', '3'],    
    ['4', '5', '6'],    
    ['7', '8', '9'],
]

pin = '' 

# first window
root = Tk()
root.title("PIN")
root.configure(bg='#132237')
# root.geometry("800x600")
root.attributes('-fullscreen',True)

labeltitle=Label(root,text='Helium Leak Detector Test',font=('bold',16),fg='white',bg='#132237')
labeltitle.grid(row=0,column=0,padx=20,pady=(20,0))

labelOP=Label(root,text='Input Operator PIN:',font=('bold',14),fg='white',bg='#132237')
labelOP.grid(row=1,column=0,columnspan=2,sticky=S)

infolabel1root=Label(root,text='V2, JTG 6/22/2021',font=('italics',8),fg='white',bg='#132237')
infolabel1root.grid(row=6,column=4,sticky=E)

error_label=Label(root,text='',font=('bold',14),fg='white',bg='#132237')
error_label.grid(row=3,column=0,columnspan=2,sticky=N)

PINdata=StringVar()

e = Entry(root,textvariable=PINdata,bg='SeaGreen3',font=('bold',14))
e.grid(row=2, column=0,columnspan=2,ipadx=20,ipady=10)

for y, row in enumerate(keys, 2):
    for x, key in enumerate(row):
        b = Button(root, text=key,font=('bold',36),fg='white', bg='firebrick3',command=lambda val=key:code(val))
        b.grid(row=(y-1), column=(x+2), ipadx=10, ipady=10)
        
        bstar = Button(root, text='DONE', font=('bold',18),command=lambda val=key:code('#'),fg='white',bg="firebrick4")
        bstar.grid(row=4, column=4, ipadx=10, ipady=10)
        
        bzero = Button(root, text='0', font=('bold',36),fg='white', bg='firebrick3',command=lambda val=key:code('0'))
        bzero.grid(row=4, column=3, ipadx=10, ipady=10)
        
        bback = Button(root, text='BACK', font=('bold',18),command=lambda val=key:code('*'),fg='white',bg="firebrick4")
        bback.grid(row=4, column=2, ipadx=10, ipady=10)
    
    # exits PIN program
    def kill_PIN():
        root.destroy()

pin_exit = Button(root, text='EXIT',font=('bold',18),command=kill_PIN,fg='white',bg="firebrick4")
pin_exit.grid(row=6, column=3,pady=5,ipadx=10, ipady=5)

# Used for better spacing on screen
labelblank=Label(root,text='              ',font=(20),fg='white',bg='#132237')
labelblank.grid(row=3,column=1,padx=10,pady=10)


# test window
def openwindow():
    
    # clears input from entry fields
    def clear_command():
        entry1.delete(0, END)
        entry2.delete(0, END)
        entry3.delete(0, END)
        entry4.delete(0, END)
        entry1.focus_set()
        return None
    
    # write to CSV if TRUE
    # write to InfluxDB if FALSE
    def influxdb():
        def run():
            date = datetime.now().strftime("%d-%B-%Y_%H-%M-%S")
            filename = date+".csv"
            FLOW_SENSOR = 23
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(FLOW_SENSOR, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            global count
            count = 0
            def countPulse(channel):
                global count
                count = count+1
            GPIO.add_event_detect(FLOW_SENSOR, GPIO.FALLING, callback=countPulse)
            with open(filename,'w',newline='') as log:
                log.write("Time,Operator,Production Order,Material #,Quantity,Serial #,Leak Rate,Inlet Pressure,Helium Flow\n")
                while (switch == True):
                    ADC_Value = ADC.ADS1256_GetAll()
                    # measured data for resistors, subject to change. Recorded in ohms
                    R1 = 4703
                    R2 = 2192
                    R3 = 2194
                    R4 = 997
                    Vout2 = ADC_Value[2]*5.0/0x7fffff
                    Vout3 = ADC_Value[3]*5.0/0x7fffff
                    Vs2 = ((Vout2)*((R1+R2)/(R2)))
                    Vs3 = ((Vout3)*((R3+R4)/(R4)))
                    interpFLVs2 = FL(Vs2)
                    interpIPVs3 = IP(Vs3)
                    FLVs2 = interpFLVs2*(1.0)
                    IPVs3 = interpIPVs3*(1.0)
                    now = datetime.now()
#                     time.sleep(1)
                    countfinal = count
                    count = 0
                    log.write("{0},{1},{2},{3},{4},{5},{6},{7},{8}\n".format(now,str(UserName),str(WO.get()),str(MAT.get()),str(QTY.get()),str(SER.get()),FLVs2,IPVs3,countfinal))
#                     infolabel2.config(text='Inlet Pressure:\n%.1E'% IPVs3)
#                     infolabel3.config(text='Leak Rate:\n%.2E'% FLVs2)
                    time.sleep(0.05)
                if switch == False:
#                     infolabel2.config(text='Inlet Pressure:')
#                     infolabel3.config(text='Leak Rate:')
                    emptylabel2.config(text='STOPPED',fg='red')
                    window.after(2000, clear_label)
                    file_path = r'/home/pi/Data_Logging/'+filename
                    csvReader = pd.read_csv(file_path)
                    while True:
                        for row_index, row in csvReader.iterrows():
                            tag1 = row[1]
                            tag2 = row[2]
                            tag3 = row[3]
                            tag4 = row[4]
                            tag5 = row[5]
                            fieldValue1 = row[6]
                            fieldValue2 = row[7]
                            fieldValue3 = row[8]
                            write_api = client.write_api(write_options=SYNCHRONOUS)
                            json_body = [
                                {
                                    "measurement": "TEST4",
#                                     "time": row[0],
                                    "tags": {
                                        "Operator": tag1,
                                        "Production Order": tag2,
                                        "Material #": tag3,
                                        "Quantity": tag4,
                                        "Serial #": tag5
                                                    },
                                    "fields": {
                                            "Leak Rate": fieldValue1,
                                            "Inlet Pressure": fieldValue2,
                                            "Helium Flow": fieldValue3
                                    }
                                }
                            ]
#                         print(json_body)
                            write_api.write(bucket,org,json_body)
                            emptylabel4.config(text='UPLOADING...\n{:.0f}%'.format((row_index/len(csvReader))*100),fg='yellow')
                            # when the upload has made it through every line of the CSV file and uploaded it to InfluxDB
                            if row_index == len(csvReader.index)-1:
                                emptylabel4.config(text='DONE',fg='red')
                                window.after(3000, clear_label)
                                break
                        break
        thread = threading.Thread(target=run)
        thread.start()        
    
    # begins test
    def switch_on():
        global switch  
        switch = True  
        print ('Test Started')
        emptylabel2.config(text='TESTING...',fg='SeaGreen3')
        influxdb()
    
    # ends test
    def switch_off():
        global switch  
        switch = False
        print('Test Ended')
        emptylabel2.config(text='')
    
    # clears live label
    def clear_label():
        emptylabel2.config(text='')
        emptylabel4.config(text='')
    
    # exits program
    def kill():
        global switch  
        switch = False
        root.destroy()

    # creates second window on top of first widnow
    window = Toplevel(root)
    window.title("Helium Leak Detector")
#     window.geometry("800x600")
    window.attributes('-fullscreen',True)
    window.configure(bg='#132237')

    label0=Label(window,text='Helium Leak Detector Test',font=('bold',18),fg='white',bg='#132237')
    label0.grid(row=0,column=0,padx=20,pady=(20,10))

    labelname=Label(window,text='Logged in as: {}'.format(UserName),wraplength=350,font=('bold',14),fg='gray80',bg='#132237')
    labelname.grid(row=1,column=0)

    label1=Label(window,text='Production Order:',font=('bold',16),fg='white',bg='#132237')
    label1.grid(row=2,column=0,padx=5,pady=10)

    label3=Label(window,text='Material #:',font=('bold',16),fg='white',bg='#132237')
    label3.grid(row=3,column=0,padx=5,pady=10)

    label2=Label(window,text='Production Order Quantity:',font=('bold',16),fg='white',bg='#132237')
    label2.grid(row=4,column=0,padx=5,pady=10)

    label4=Label(window,text='Serial # (if applicable):',font=('bold',16),fg='white',bg='#132237')
    label4.grid(row=5,column=0,padx=5,pady=10)

    infolabel1=Label(window,text='V2, JTG 6/22/2021',font=('italics',8),fg='white',bg='#132237')
    infolabel1.grid(row=6,column=2,sticky=S)

# for a live read of the Inlet Pressure and Leak Rate, uncomment these sections.
# not particularly necessary since the readout is already on the machine
#     infolabel2 = Label(window,text='Inlet Pressure:',fg='SeaGreen3',font=('bold',16),bg='#132237')
#     infolabel2.grid(row=5,column=2)
#     
#     infolabel3 = Label(window,text='Leak Rate:',fg='SeaGreen3',font=('bold',16),bg='#132237')
#     infolabel3.grid(row=6,column=2)
    
    emptylabel2 = Label(window,text='',fg='yellow',font=('bold',20),bg='#132237')
    emptylabel2.grid(row=0,column=1,rowspan=2)

    emptylabel4 = Label(window,text='',fg='red',font=('bold',20),bg='#132237')
    emptylabel4.grid(row=0,column=2,rowspan=2)

    WO=StringVar()
    QTY=StringVar()
    MAT=StringVar()
    SER=StringVar()

    entry1 = Entry(window, textvariable=WO)
    entry1.grid(row = 2,column = 1,ipadx=30,ipady=5)
    entry1.focus_set()

    entry3 = Entry(window, textvariable=MAT)
    entry3.grid(row = 3,column = 1,ipadx=30,ipady=5)
    
    entry2 = Entry(window, textvariable=QTY)
    entry2.grid(row = 4,column = 1,ipadx=30,ipady=5)

    entry4 = Entry(window, textvariable=SER)
    entry4.grid(row = 5,column = 1,ipadx=30,ipady=5)

    # function to skip to next entry box when barcode has been scanned
    def get_key(event):
        global barcode
        if event.keysym == 'Return':
            if len(WO.get()) > 0:
                entry3.focus()
            if len(MAT.get()) > 0:
                entry2.focus()
            if len(QTY.get()) > 0:
                entry4.focus()
            if len(SER.get()) > 0:
                begin_button.focus()
            
    barcode = ''
    
    window.bind('<Key>',get_key)

    clear_button = Button(window, text="Clear All" ,font=('bold',16),fg='white', bg='firebrick4',command=clear_command)
    clear_button.grid(row=3,column=2, padx=20,pady=5,ipadx=10, ipady=10)

    exit_button = Button(window, text="EXIT" ,font=('bold',16),fg='white', bg='firebrick4',command=kill)
    exit_button.grid(row=4,column=2,padx=20,pady=5,ipadx=10, ipady=10)

    begin_button = Button(window, text="Start Recording" ,font=('bold',20),fg='white', bg='firebrick4',command=switch_on)
    begin_button.grid(row=6,column=0,pady=25,padx=15,ipady=20)

    end_button = Button(window, text="End Recording" ,font=('bold',20),fg='white', bg='firebrick4',command=switch_off)
    end_button.grid(row=6,column=1,pady=25, padx=15,ipady=20)

mainloop()
