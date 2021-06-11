from datetime import datetime
import ADS1256

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

def open():
    window = Tk()
    window.title("Helium Leak Detector")
    window.geometry("575x275")
    window.configure(bg='#132237')
    window.eval('tk::PlaceWindow . center')

    label0=Label(window,text='Helium Leak Detector Test',font=(24),fg='white',bg='#132237')
    label0.grid(row=0,column=0,padx=10,pady=10)

    labelname=Label(window,text='Logged in as:\n {}'.format(list2[list1.index(pin)]),font=(10),fg='white',bg='#132237')
    labelname.grid(row=1,column=0)

    label1=Label(window,text='Production Order:',fg='white',bg='#132237')
    label1.grid(row=2,column=0,padx=5,pady=10)

    label2=Label(window,text='Production Order Quantity:',fg='white',bg='#132237')
    label2.grid(row=3,column=0,padx=5,pady=10)

    label3=Label(window,text='Material #:',fg='white',bg='#132237')
    label3.grid(row=4,column=0,padx=5,pady=10)

    label4=Label(window,text='Serial # (if applicable):',fg='white',bg='#132237')
    label4.grid(row=5,column=0,padx=5,pady=10)

    emptylabel2 = Label(window,text='',fg='dodger blue',font=('bold',16),bg='#132237')
    emptylabel2.grid(row=0,column=1)

    emptylabel4 = Label(window,text='',fg='red',font=('bold',16),bg='#132237')
    emptylabel4.grid(row=0,column=2)

    data1=StringVar()
    data2=StringVar()
    data3=StringVar()
    data4=StringVar()

    entry1 = Entry(window, textvariable=data1)
    entry1.grid(row = 2,column = 1)
    entry1.focus_set()

    entry2 = Entry(window, textvariable=data2)
    entry2.grid(row = 3,column = 1)

    entry3 = Entry(window, textvariable=data3)
    entry3.grid(row = 4,column = 1)

    entry4 = Entry(window, textvariable=data4)
    entry4.grid(row = 5,column = 1)

    def clear_command():
        entry1.delete(0, END)
        entry2.delete(0, END)
        entry3.delete(0, END)
        entry4.delete(0, END)
        return None

    def influxdb():
        def run():
            while (switch == True):
                ADC_Value = ADC.ADS1256_GetAll()
                write_api = client.write_api(write_options=SYNCHRONOUS)
                point = Point("Helium Leak Detector")\
                    .tag("Operator", "{}".format(list2[list1.index(pin)]))\
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
        emptylabel4.config(text='STOPPED')
        window.after(2000, clear_label)
        
    def clear_label():
        emptylabel4.config(text='')
        
    def kill():
     global switch  
     switch = False 
     window.destroy()

    clear_button = Button(window, text="Clear All" ,fg='white', bg='firebrick3',command=clear_command)
    clear_button.grid(row=4,column=2, pady = 5)

    exit_button = Button(window, text="EXIT" ,fg='white', bg='firebrick4',command=kill)
    exit_button.grid(row=5,column=2,pady=5)

    begin_button = Button(window, text="Start Recording" ,fg='white', bg='firebrick3',command=switch_on)
    begin_button.grid(row=2,column=2,pady = 5, padx=15)

    end_button = Button(window, text="End Recording" ,fg='white', bg='firebrick3',command=switch_off)
    end_button.grid(row=3,column=2,pady = 5, padx=15)


    mainloop()
    
    
def code(value):
    
    global pin
    global list1, list2  

    if value == '*':
        pin = pin[:-1]
        e.delete('0', 'end')
        e.insert('end', pin)

    elif value == '#':


# examples of pins and names  
        list1 = ['3529','4324','5452','0000','1234']
        list2 = ['John Smith', 'Joe Smith', 'Don Julio', 'Ron Burgandy','Jesse Greyshock']

        if pin in list1:
            root.destroy()
            open()
            print("PIN OK")
        else:
            print("PIN ERROR!", pin)
            pin = ''
            e.delete('0', 'end')

    else:
        pin += value
        e.insert('end', value)

keys = [
    ['1', '2', '3'],    
    ['4', '5', '6'],    
    ['7', '8', '9'],
]

pin = '' 

root = Tk()
root.title("PIN")
root.eval('tk::PlaceWindow . center')


labelOP=Label(root,text='Input Operator PIN:',font=(12))
labelOP.grid(row=0,column=0,columnspan=3,padx=5,pady=10)


global PINdata
PINdata=StringVar()

e = Entry(root,textvariable=PINdata)
e.grid(row=1, column=0, columnspan=3, ipady=5)

for y, row in enumerate(keys, 2):
    for x, key in enumerate(row):
        b = Button(root, text=key,font=('bold',16),command=lambda val=key:code(val))
        b.grid(row=y, column=x, ipadx=10, ipady=10)
        
        bstar = Button(root, text='DONE', font=('bold',8),command=lambda val=key:code('#'),bg="palegreen1")
        bstar.grid(row=5, column=2, ipadx=10, ipady=10)
        
        bback = Button(root, text='0', font=('bold',16),command=lambda val=key:code('0'))
        bback.grid(row=5, column=1, ipadx=10, ipady=10)
        
        bback = Button(root, text='BACK', font=('bold',8),command=lambda val=key:code('*'),bg="khaki")
        bback.grid(row=5, column=0, ipadx=10, ipady=10)


mainloop()