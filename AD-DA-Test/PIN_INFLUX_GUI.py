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
#     window.geometry("575x275")
    window.attributes('-fullscreen',True)
    window.configure(bg='#132237')
#     window.eval('tk::PlaceWindow . center')

    label0=Label(window,text='Helium Leak Detector Test',font=('bold',18),fg='white',bg='#132237')
    label0.grid(row=0,column=0,padx=20,pady=(20,10))

    labelname=Label(window,text='Logged in as: {}'.format(list2[list1.index(pin)]),wraplength=300,font=('bold',16),fg='gray90',bg='#132237')
    labelname.grid(row=1,column=0)

    label1=Label(window,text='Production Order:',font=('bold',16),fg='white',bg='#132237')
    label1.grid(row=2,column=0,padx=5,pady=10)

    label2=Label(window,text='Production Order Quantity:',font=('bold',16),fg='white',bg='#132237')
    label2.grid(row=3,column=0,padx=5,pady=10)

    label3=Label(window,text='Material #:',font=('bold',16),fg='white',bg='#132237')
    label3.grid(row=4,column=0,padx=5,pady=10)

    label4=Label(window,text='Serial # (if applicable):',font=('bold',16),fg='white',bg='#132237')
    label4.grid(row=5,column=0,padx=5,pady=10)
    
    infolabel1=Label(window,text='V1, JTG 6/14/2021',font=('italics',8),fg='white',bg='#132237')
    infolabel1.grid(row=6,column=2,sticky=S)

    emptylabel2 = Label(window,text='',fg='yellow',font=('bold',20),bg='#132237')
    emptylabel2.grid(row=1,column=1)

    emptylabel4 = Label(window,text='',fg='red',font=('bold',20),bg='#132237')
    emptylabel4.grid(row=1,column=2)

    data1=StringVar()
    data2=StringVar()
    data3=StringVar()
    data4=StringVar()

    entry1 = Entry(window, textvariable=data1)
    entry1.grid(row = 2,column = 1,ipadx=30,ipady=5)
    entry1.focus_set()

    entry2 = Entry(window, textvariable=data2)
    entry2.grid(row = 3,column = 1,ipadx=30,ipady=5)

    entry3 = Entry(window, textvariable=data3)
    entry3.grid(row = 4,column = 1,ipadx=30,ipady=5)

    entry4 = Entry(window, textvariable=data4)
    entry4.grid(row = 5,column = 1,ipadx=30,ipady=5)

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

    clear_button = Button(window, text="Clear All" ,font=('bold',16),fg='white', bg='firebrick4',command=clear_command)
    clear_button.grid(row=3,column=2, padx=20,pady=5,ipadx=10, ipady=10)

    exit_button = Button(window, text="EXIT" ,font=('bold',16),fg='white', bg='firebrick4',command=kill)
    exit_button.grid(row=4,column=2,padx=20,pady=5,ipadx=10, ipady=10)

    begin_button = Button(window, text="Start Recording" ,font=('bold',20),fg='white', bg='firebrick4',command=switch_on)
    begin_button.grid(row=6,column=0,pady=25,padx=15,ipady=20)

    end_button = Button(window, text="End Recording" ,font=('bold',20),fg='white', bg='firebrick4',command=switch_off)
    end_button.grid(row=6,column=1,pady=25, padx=15,ipady=20)


    mainloop()
    
    
def code(value):
    
    global pin
    global list1, list2  

    def default_label():
        error_label.config(text='')

    if value == '*':
        pin = pin[:-1]
        e.delete('0', 'end')
        e.insert('end', pin)

    elif value == '#':


        # examples of pins and names  
        list1 = ['3529','4321','1394','0000','1234']
        list2 = ['John Smith', 'Joe Smith', 'Rob Mrozek', 'Jim Smith','Jesse Greyshock']

        if pin in list1:
            root.destroy()
            open()
#             print("PIN OK")
        else:
#             print("PIN ERROR!", pin)
            error_label.config(text='PIN ERROR!')
            root.after(1500, default_label)
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
root.configure(bg='#132237')
# width=root.winfo_screenwidth()
# height=root.winfo_screenheight()
root.attributes('-fullscreen',True)
# root.eval('tk::PlaceWindow . center')

labeltitle=Label(root,text='Helium Leak Detector Test',font=('bold',16),fg='white',bg='#132237')
labeltitle.grid(row=0,column=0,padx=20,pady=(20,0))

labelOP=Label(root,text='Input Operator PIN:',font=('bold',14),fg='white',bg='#132237')
labelOP.grid(row=1,column=0,columnspan=2,sticky=S)

infolabel1=Label(root,text='V1, JTG 6/14/2021',font=('italics',8),fg='white',bg='#132237')
infolabel1.grid(row=6,column=4,sticky=E)

error_label=Label(root,text='',font=('bold',14),fg='white',bg='#132237')
error_label.grid(row=3,column=0,columnspan=2,sticky=N)

global PINdata
PINdata=StringVar()

e = Entry(root,textvariable=PINdata,bg='SeaGreen3',font=('bold',14))
e.grid(row=2, column=0,columnspan=2,ipadx=20,ipady=10)

for y, row in enumerate(keys, 2):
    for x, key in enumerate(row):
        b = Button(root, text=key,font=('bold',36),fg='white', bg='firebrick3',command=lambda val=key:code(val))
        b.grid(row=(y-1), column=(x+2), ipadx=10, ipady=10)
        
        bstar = Button(root, text='DONE', font=('bold',18),command=lambda val=key:code('#'),fg='white',bg="firebrick4")
        bstar.grid(row=4, column=4, ipadx=10, ipady=10)
        
        bback = Button(root, text='0', font=('bold',36),fg='white', bg='firebrick3',command=lambda val=key:code('0'))
        bback.grid(row=4, column=3, ipadx=10, ipady=10)
        
        bback = Button(root, text='BACK', font=('bold',18),command=lambda val=key:code('*'),fg='white',bg="firebrick4")
        bback.grid(row=4, column=2, ipadx=10, ipady=10)

    def kill_PIN():
        root.destroy()

# labelblank=Label(root,text='',font=(6),fg='white',bg='#132237')
# labelblank.grid(row=6,column=1,columnspan=3)

pin_exit = Button(root, text='EXIT',font=('bold',18),command=kill_PIN,fg='white',bg="firebrick4")
pin_exit.grid(row=6, column=3,pady=5,ipadx=10, ipady=5)

labelblank=Label(root,text='              ',font=(20),fg='white',bg='#132237')
labelblank.grid(row=3,column=1,padx=10,pady=10)


mainloop()