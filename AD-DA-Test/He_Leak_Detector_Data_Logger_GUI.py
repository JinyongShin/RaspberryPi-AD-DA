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
import csv
from pytz import timezone

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
measurement = "TEST7" # change to write to a different measurement filter
client = InfluxDBClient(url="http://glin.saxire.net", token=token)

# Voltage and Leak Rate conversion data pulled from Detector manual
Volts = [0,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.00,1.05,1.10,1.15,1.20,1.25,1.30,1.35,1.40,1.45,1.50,1.55,1.60,1.65,1.70,1.75,1.80,1.85,1.90,1.95,2.00,2.05,2.10,2.15,2.20,2.25,2.30,2.35,2.40,2.45,2.50,2.55,2.60,2.65,2.70,2.75,2.80,2.85,2.90,2.95,3.00,3.05,3.10,3.15,3.20,3.25,3.30,3.35,3.40,3.45,3.50,3.55,3.60,3.65,3.70,3.75,3.80,3.85,3.90,3.95,4.00,4.05,4.10,4.15,4.20,4.25,4.30,4.35,4.40,4.45,4.50,4.55,4.60,4.65,4.70,4.75,4.80,4.85,4.90,4.95,5.00,5.10,5.20,5.30,5.40,5.50,5.60,5.70,5.80,5.90,6.00,6.10,6.20,6.30,6.40,6.50,6.60,6.70,6.80,6.90,7.00,7.10,7.20,7.30,7.40,7.50,7.60,7.70,7.80,7.90,8.00]
Signal_He_FL = [0,3.07E-12,1.12E-11,2.08E-11,3.20E-11,4.51E-11,6.03E-11,7.80E-11,9.84E-11,1.22E-10,1.49E-10,1.80E-10,2.16E-10,2.57E-10,3.04E-10,3.57E-10,4.18E-10,4.88E-10,5.67E-10,6.56E-10,7.58E-10,8.74E-10,1.00E-09,1.15E-09,1.32E-09,1.51E-09,1.73E-09,1.97E-09,2.25E-09,2.56E-09,2.91E-09,3.30E-09,3.75E-09,4.25E-09,4.82E-09,5.46E-09,6.18E-09,6.99E-09,7.91E-09,8.93E-09,1.01E-08,1.14E-08,1.29E-08,1.45E-08,1.64E-08,1.85E-08,2.08E-08,2.35E-08,2.64E-08,2.98E-08,3.35E-08,3.77E-08,4.25E-08,4.78E-08,5.38E-08,6.05E-08,6.81E-08,7.66E-08,8.61E-08,9.68E-08,1.09E-07,1.22E-07,1.38E-07,1.55E-07,1.74E-07,1.95E-07,2.19E-07,2.46E-07,2.77E-07,3.11E-07,3.49E-07,3.92E-07,4.40E-07,4.95E-07,5.55E-07,6.24E-07,7.00E-07,7.86E-07,8.83E-07,9.91E-07,1.11E-06,1.25E-06,1.40E-06,1.57E-06,1.77E-06,1.98E-06,2.23E-06,2.50E-06,2.81E-06,3.15E-06,3.53E-06,3.97E-06,4.45E-06,5.00E-06,5.61E-06,6.29E-06,7.06E-06,7.93E-06,8.89E-06,9.98E-06,1.26E-05,1.58E-05,1.99E-05,2.51E-05,3.16E-05,3.98E-05,5.01E-05,6.31E-05,7.94E-05,1.00E-04,1.26E-04,1.58E-04,2.00E-04,2.51E-04,3.16E-04,3.98E-04,5.01E-04,6.31E-04,7.94E-04,1.00E-03,1.26E-03,1.58E-03,2.00E-03,2.51E-03,3.16E-03,3.98E-03,5.01E-03,6.31E-03,7.94E-03,1.00E-02]
Signal_He_GL = [0,3.07E-10,1.12E-09,2.08E-09,3.20E-09,4.51E-09,6.03E-09,7.80E-09,9.84E-09,1.22E-08,1.49E-08,1.80E-08,2.16E-08,2.57E-08,3.04E-08,3.57E-08,4.18E-08,4.88E-08,5.67E-08,6.56E-08,7.58E-08,8.74E-08,1.00E-07,1.15E-07,1.32E-07,1.51E-07,1.73E-07,1.97E-07,2.25E-07,2.56E-07,2.91E-07,3.30E-07,3.75E-07,4.25E-07,4.82E-07,5.46E-07,6.18E-07,6.99E-07,7.91E-07,8.93E-07,1.01E-06,1.14E-06,1.29E-06,1.45E-06,1.64E-06,1.85E-06,2.08E-06,2.35E-06,2.64E-06,2.98E-06,3.35E-06,3.77E-06,4.25E-06,4.78E-06,5.38E-06,6.05E-06,6.81E-06,7.66E-06,8.61E-06,9.68E-06,1.09E-05,1.22E-05,1.38E-05,1.55E-05,1.74E-05,1.95E-05,2.19E-05,2.46E-05,2.77E-05,3.11E-05,3.49E-05,3.92E-05,4.40E-05,4.95E-05,5.55E-05,6.24E-05,7.00E-05,7.86E-05,8.83E-05,9.91E-05,1.11E-04,1.25E-04,1.40E-04,1.57E-04,1.77E-04,1.98E-04,2.23E-04,2.50E-04,2.81E-04,3.15E-04,3.53E-04,3.97E-04,4.45E-04,5.00E-04,5.61E-04,6.29E-04,7.06E-04,7.93E-04,8.89E-04,9.98E-04,1.26E-03,1.58E-03,1.99E-03,2.51E-03,3.16E-03,3.98E-03,5.01E-03,6.31E-03,7.94E-03,1.00E-02,1.26E-02,1.58E-02,2.00E-02,2.51E-02,3.16E-02,3.98E-02,5.01E-02,6.31E-02,7.94E-02,1.00E-01,1.26E-01,1.58E-01,2.00E-01,2.51E-01,3.16E-01,3.98E-01,5.01E-01,6.31E-01,7.94E-01,1.00E+00]

FL = interp1d(Volts, Signal_He_FL) # Fine Leak (main data set used for conversion)
GL = interp1d(Volts, Signal_He_GL) # Gross Leak

# estimated/recorded values used to determine the conversion of voltage to inlet pressure
Volts2 = [0,2.45,7.07,10]
Inlet_Pressure = [0,1.0E-3,2.0E2,1E3]

IP = interp1d(Volts2, Inlet_Pressure)

# PIN window 
def code(value):

    global pin
    global UserPIN, UserName
    global col0, col1, i

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
        
        try:
            """

            Access SQL database for Operator PINs
            Needs internet connection
            
            """
            
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
                
        except:
            os.chdir("/home/pi/Helium_Leak_Detector")
            
            data = []
            with open('Diamond_Turning_Operators_7_29_21.csv') as Operators_backup:
                reader = csv.reader(Operators_backup)
                for row2 in reader:
                    data.append(row2)
                    
            col0 = [x[0] for x in data]
            col1 = [x[1] for x in data]
            
            if pin in col0:
                
                for i in range(0,len(col0)):
                    if col0[i] == pin:
                        UserName = str(col1[i])
                        os.chdir("/home/pi/Data_Logging")
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
root.attributes('-fullscreen',True)

# labels
labeltitle=Label(root,text='He Leak - Data Collection',font=('bold',16),fg='white',bg='#132237')
labeltitle.grid(row=0,column=0,padx=20,pady=(20,0))

labelOP=Label(root,text='Input Operator PIN:',font=('bold',14),fg='white',bg='#132237')
labelOP.grid(row=1,column=0,columnspan=2,sticky=S)

infolabel1root=Label(root,text='V2, JTG 7/16/2021',font=('italics',8),fg='white',bg='#132237')
infolabel1root.grid(row=6,column=4,sticky=E)

error_label=Label(root,text='',font=('bold',14),fg='white',bg='#132237')
error_label.grid(row=3,column=0,columnspan=2,sticky=N)

# Used for better spacing on touchscreen
labelblank=Label(root,text='              ',font=(20),fg='white',bg='#132237')
labelblank.grid(row=3,column=1,padx=10,pady=10)

# turn PIN box to string
PINdata=StringVar()

# buttons
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


# Window used to upload tests to InfluxDB that failed to upload because of internet connection, etc.
def failedtestwindow():
    
    def failed_test():
        def upload():
            try:
                # change directory to grab the text document that has the names of CSV files saved
                os.chdir("/home/pi/Helium_Leak_Detector")
                
                with open('Failed_Uploads_to_InfluxDB.txt','r+') as f:
                    
                    # if the document is empty, "NO TESTS TO UPLOAD" will display
                    if os.stat("Failed_Uploads_to_InfluxDB.txt").st_size == 0:
                        emptylabel7.config(text='NO TESTS TO UPLOAD',fg='yellow')
            
                    else:
                        for line in f:
                            filename = str(line).rstrip("\n") # (ex. 29-July-2021_13-37-44.csv)
                            
                            file_path = r'/home/pi/Data_Logging/'+filename
                            df = pd.read_csv(file_path)
                            df['He Flow Avg'] = df.He_Flow_Rate.rolling(window=10).mean()
                            df['He Flow Avg'] = df['He Flow Avg'].fillna(0)
                            # moving average flow rate for smoother curve in InfluxDB
                                                   
                            while True:
                                
                                for row_index, row in df.iterrows(): # reading CSV file
                                    tag1 = row[1]
                                    tag2 = row[2]
                                    tag3 = row[3]
                                    tag4 = row[4]
                                    tag5 = row[5]
                                    fieldValue1 = row[6]
                                    fieldValue2 = row[7]
                                    fieldValue3 = row[9]
                                    write_api = client.write_api(write_options=SYNCHRONOUS)
                                    json_body = [
                                        {
                                            "measurement": measurement,
                                            "time": row[0],
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
                                    write_api.write(bucket,org,json_body)
                                    emptylabel6.config(text=filename,fg='seagreen3')
                                    # shows the % of CSV data uploaded to influxdb
                                    emptylabel5.config(text='UPLOADING...\n{:.0f}%'.format((row_index/len(df))*100),fg='yellow')
                                break
                        emptylabel7.config(text='TEST SUCCESSFULLY UPLOADED',fg='seagreen3')
                        time.sleep(3)
                        emptylabel5.config(text='')
                        emptylabel6.config(text='')
                        emptylabel7.config(text='')
                        f.truncate(0)
                        
            except:
                # exception thrown when internet connection can't be achieved
                emptylabel7.config(text='UNABLE TO UPLOAD.\nCHECK NETOWRK\nCONNECTION.',fg='red')
                time.sleep(3)
                emptylabel7.config(text='')
        
        thread2 = threading.Thread(target=upload)
        thread2.start()
    
    def back_to_test():
        # when leaving to go back to main page, directory is changed back to default
        os.chdir("/home/pi/Data_Logging")
        window2.destroy()
        
    window2 = Toplevel(root)
    window2.title("Failed Test Window")
    window2.attributes('-fullscreen',True)
    window2.configure(bg='#132237')
    
    #labels
    labeltitle3=Label(window2,text='He Leak - Data Collection',font=('bold',18),fg='white',bg='#132237')
    labeltitle3.grid(row=0,column=0,padx=20,pady=(20,10))
    
    emptylabel5 = Label(window2,fg='red',font=('bold',20),bg='#132237')
    emptylabel5.grid(row=1,column=1,rowspan=2)
    
    emptylabel6 = Label(window2,fg='red',font=('bold',16),bg='#132237')
    emptylabel6.grid(row=2,column=1,rowspan=2)
    
    emptylabel7 = Label(window2,fg='red',borderwidth=1,relief="raised",font=('bold',16),bg='#132237')
    emptylabel7.grid(row=3,column=1,pady=25)
    
    statuslabel = Label(window2,text='STATUS:',fg='white',borderwidth=1,relief="raised",font=('bold',16),bg='#132237')
    statuslabel.grid(row=3,column=0,rowspan=2,pady=25)
    
    #buttons
    upload_button = Button(window2, text="UPLOAD" ,font=('bold',20),fg='white', bg='firebrick4',command=failed_test)
    upload_button.grid(row=1,column=0,pady=25,padx=15,ipady=20)
    
    back2_button = Button(window2, text="BACK" ,font=('bold',20),fg='white', bg='firebrick4',command=back_to_test)
    back2_button.grid(row=2,column=0,padx=20,pady=5,ipadx=10, ipady=10)
    
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
            # GPIO23 is the signal pin that connects from the Pi to the Leak Detector.
            # If you change the pin, change the script
            FLOW_SENSOR = 23
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(FLOW_SENSOR, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            
            # sets inital count to 0
            global count
            count = 0
            
            # counts the revolutions of the paddlewheel inside the flowmeter roughly every 0.1 second
            def countPulse(channel):
                global count
                count = count+1
                
            GPIO.add_event_detect(FLOW_SENSOR, GPIO.FALLING, callback=countPulse)
            
            # name csv file with timestamp
            date = datetime.now().strftime("%d-%B-%Y_%H-%M-%S")
            filename = date+".csv"
            
            # write headers for CSV file
            with open(filename,'w',newline='') as log:
                log.write("Time,Operator,Production Order,Material #,Quantity,Serial #,Leak Rate,Inlet Pressure,He_Flow_Rate\n")  
                
                while (switch == True):      
                        
                    # call to ADC board
                    ADC_Value = ADC.ADS1256_GetAll()
                    
                    # measured data for resistors, subject to change. Recorded in ohms
                    R1 = 4703
                    R2 = 2192
                    R3 = 2194
                    R4 = 997
                    
                    # reads voltage from AD/DA board
                    Vout2 = ADC_Value[2]*5.0/0x7fffff
                    Vout3 = ADC_Value[3]*5.0/0x7fffff
                    
                    # convert back to actual voltage after going through divider
                    Vs2 = ((Vout2)*((R1+R2)/(R2)))
                    Vs3 = ((Vout3)*((R3+R4)/(R4)))
                    
                    # match voltage to corresponding leak rate and inlet pressure
                    interpFLVs2 = FL(Vs2)
                    interpIPVs3 = IP(Vs3)
                    FLVs2 = interpFLVs2*(1.0)
                    IPVs3 = interpIPVs3*(1.0)
                    
                    # time stamp is in UTC, but will be uploaded to influxdb with local time
                    UTC = timezone('UTC')
                    now = datetime.now(UTC)
                    
                    # Flow counter record and reset
                    countfinal = count
                    count = 0
                    
                    # write to CSV
                    log.write("{0},{1},{2},{3},{4},{5},{6},{7},{8}\n".format(now,str(UserName),str(WO.get()),str(MAT.get()),str(QTY.get()),str(SER.get()),FLVs2,IPVs3,countfinal))
                    
                    # time.sleep used to make the script get roughly 10 data points a second
                    time.sleep(0.05)
                
                if switch == False:
                    
                    """
                    The newly written CSV file is stored in the Data_Logging folder.
                    When the swith turns to False, the script pulls that CSV file and uploads it to InfluxDB.
                    
                    MUST HAVE INTERNET CONNECTION FOR THIS STEP!
                    
                    If no internet connection, the exeption will be thrown and display "UPLOAD FAILED" on the screen.
                    See "failedtestwindow()" to upload a failed test.
                    """
                    
                    try: 
                        emptylabel2.config(text='STOPPED',fg='red')
                        window.after(2000, clear_label1)
                        file_path = r'/home/pi/Data_Logging/'+filename 
                        df = pd.read_csv(file_path)
                        df['He Flow Avg'] = df.He_Flow_Rate.rolling(window=10).mean()
                        df['He Flow Avg'] = df['He Flow Avg'].fillna(0)
                        # moving average flow rate for smoother curve in InfluxDB
                       
                        while True:
                            
                            for row_index, row in df.iterrows(): # reading CSV file
                                tag1 = row[1]
                                tag2 = row[2]
                                tag3 = row[3]
                                tag4 = row[4]
                                tag5 = row[5]
                                fieldValue1 = row[6]
                                fieldValue2 = row[7]
                                fieldValue3 = row[9]
                                
                                # contacts Influxdb client
                                write_api = client.write_api(write_options=SYNCHRONOUS)
                                
                                json_body = [
                                    {
                                        "measurement": measurement,
                                        "time": row[0],
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
                                
                                # writes point
                                write_api.write(bucket,org,json_body)
                                
                                # shows the % of CSV data uploaded to influxdb
                                emptylabel4.config(text='UPLOADING...\n{:.0f}%'.format((row_index/len(df))*100),fg='yellow')
                                
                                # when the upload has made it through every line of the CSV file and uploaded it to InfluxDB
                                if row_index == len(df.index)-1:
                                    emptylabel4.config(text='DONE',fg='red')
                                    # the GPIO sometimes throws an error when multiple tests are tried during same session
                                    # log back in to do another test
                                    # RuntimeError: Conflicting edge detection already enabled for this GPIO channel
                                    break
                            
                            break
                        
                    except:
                        emptylabel2.config(text='STOPPED',fg='red')
                        window.after(500, clear_label1)
                        
                        # if there is no internet connection, Error message appears in the window
                        time.sleep(0.5)
                        emptylabel3.config(text='UPLOAD FAILED',fg='red')
                        
                        os.chdir("/home/pi/Helium_Leak_Detector")
                        
                        # writes the name of the CSV file that failed to upload to influxDB to a text document
                        # CSV file is locally saved in the Data_Logging folder
                        with open('Failed_Uploads_to_InfluxDB.txt','a',newline='') as Failed_Upload:
                            Failed_Upload.write('{}\n'.format(filename)) # \n used for spacing on txt document
                            
                        os.chdir("/home/pi/Data_Logging")
                        
        thread = threading.Thread(target=run)
        thread.start()

    # begins test
    def switch_on():
        global switch  
        switch = True
        emptylabel2.config(text='TESTING...',fg='SeaGreen3')
        
        # stopwatch to see how long a test has been running for
        def stopwatch():
            second = 0    
            minute = 0    
            hours = 0
            
            while (switch == True):
                emptylabel4.config(text='%d : %d'%(minute,second),fg='SeaGreen3',borderwidth=1,relief="raised",font=('bold',16))
                time.sleep(1)   
                second+=1    
                if(second == 60):    
                    second = 0    
                    minute+=1
                    
        thread3 = threading.Thread(target=stopwatch)
        thread3.start()
        
        influxdb()
    
    # ends test
    def switch_off():
        global switch  
        switch = False
        emptylabel2.config(text='')
                
    # clears live labels
    def clear_label1():
        emptylabel2.config(text='')
        emptylabel4.config(text='')
        
    # exits program
    def kill():
        global switch  
        switch = False
        root.destroy()
    
    # function to skip to next entry box when barcode has been scanned
    def get_key(event):
        if event.keysym == 'Return':
            if len(WO.get()) > 0:
                entry3.focus()
            if len(MAT.get()) > 0:
                entry2.focus()
            if len(QTY.get()) > 0:
                entry4.focus()
            if len(SER.get()) > 0:
                begin_button.focus()
    
    # creates second window on top of first widnow
    window = Toplevel(root)
    window.title("Helium Leak Detector")
    window.attributes('-fullscreen',True)
    window.configure(bg='#132237')
    
    # labels
    labeltitle2=Label(window,text='He Leak - Data Collection',font=('bold',18),fg='white',bg='#132237')
    labeltitle2.grid(row=0,column=0,padx=20,pady=(20,10))
    
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

    infolabel1=Label(window,text='V2, JTG 7/16/2021',font=('italics',8),fg='white',bg='#132237')
    infolabel1.grid(row=6,column=2,sticky=S)
    
    emptylabel2 = Label(window,fg='yellow',font=('bold',20),bg='#132237')
    emptylabel2.grid(row=0,column=1,rowspan=2)

    emptylabel3 = Label(window,fg='red',font=('bold',20),bg='#132237')
    emptylabel3.grid(row=0,column=1,rowspan=2, columnspan=2)

    emptylabel4 = Label(window,fg='red',font=('bold',20),bg='#132237')
    emptylabel4.grid(row=0,column=2,rowspan=2)


    # turns all entry boxes into string variables
    WO=StringVar()
    QTY=StringVar()
    MAT=StringVar()
    SER=StringVar()
    
    # calls get_key function to skip line when barcode is scanned
    window.bind('<Key>',get_key)


    # entry boxes
    entry1 = Entry(window, textvariable=WO)
    entry1.grid(row = 2,column = 1,ipadx=30,ipady=5)
    entry1.focus_set()

    entry3 = Entry(window, textvariable=MAT)
    entry3.grid(row = 3,column = 1,ipadx=30,ipady=5)
    
    entry2 = Entry(window, textvariable=QTY)
    entry2.grid(row = 4,column = 1,ipadx=30,ipady=5)

    entry4 = Entry(window, textvariable=SER)
    entry4.grid(row = 5,column = 1,ipadx=30,ipady=5)

    # buttons
    clear_button = Button(window, text="Clear All" ,font=('bold',16),fg='white', bg='firebrick4',command=clear_command)
    clear_button.grid(row=3,column=2, padx=20,pady=5,ipadx=10, ipady=10)

    exit_button = Button(window, text="EXIT" ,font=('bold',16),fg='white', bg='firebrick4',command=kill)
    exit_button.grid(row=4,column=2,padx=20,pady=5,ipadx=10, ipady=10)

    begin_button = Button(window, text="Start Recording" ,font=('bold',20),fg='white', bg='firebrick4',command=switch_on)
    begin_button.grid(row=6,column=0,pady=25,padx=15,ipady=20)

    end_button = Button(window, text="End Recording" ,font=('bold',20),fg='white', bg='firebrick4',command=switch_off)
    end_button.grid(row=6,column=1,pady=25, padx=15,ipady=20)
    
    failed_upload_button = Button(window, text="Upload\nFailed Test" ,font=('bold',16),fg='white', bg='firebrick4',command=failedtestwindow)
    failed_upload_button.grid(row=5,column=2,rowspan=2,pady=25,padx=15,ipady=20)

mainloop()

