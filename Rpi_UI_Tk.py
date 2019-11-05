import tkinter as tk
from tkinter import messagebox
from tkinter import *
from PIL import ImageTk, Image
import paho.mqtt.client as mqtt
from threading import Thread
from google_drive_downloader import GoogleDriveDownloader as gdd
from multiprocessing import Process
import datetime
import re
import time
import sqlite3

allNotices = []

class Notice:
    def __init__(self,i, h, m, p, a):
        self.Heading = h
        self.Msg = m
        self.Publisher = p
        self.Addressee = a
        self.contestImg = i
        self.publishDate = datetime.date.today()
        self.ttl = 5
        
def destroy_notices():
    global allNotices
    for i in range(len(allNotices)):
        if(allNotices[i].ttl == 0):
            print("Removing Notice: "+allNotices[i].Heading+" at "+str(i))
            allNotices.remove(allNotices[i])
            if(len(allNotices)<=0):
                reset_nb()
            break


def newNotice(contestImg, Heading, Msg, Publisher, Addressee):
    global allNotices
    
    print('making notice object')
    notice = Notice(contestImg,Heading, Msg, Publisher, Addressee)
    print(notice.Heading+" : "+str(notice.ttl))
    allNotices.append(notice)
    print(allNotices)

    
def reset_nb():
    global BottomMain
    print('reseting NB')
    lblHeading = Label(BottomMain,font=('Arial Black',30,'bold'), text="No notice to show yet",padx=20, width=45, height=2)
    lblHeading.grid(row=0,column=0)
    lblMsg = Label(BottomMain ,font=('',25,'bold'),bg='white', padx=5, width=65, height=11, justify='center', wraplength=1300, text="")
    lblMsg.grid(row=1,column=0)
    Footer = tk.Frame(BottomMain, width=1350, height=100)
    Footer.grid(row=2,column=0)
    lblPublisher = Label(Footer,font=(15), bg="white", text="Published By:", width=50)
    lblPublisher.grid(row=0,column=0)
    lblAddressee = Label(Footer,font=(15), bg="white", text="To:", width=50)
    lblAddressee.grid(row=0,column=1)
    
def carousel():
    global allNotices
    print('carousel start')
    while 1:
        destroy_notices()
        if(len(allNotices)>0):
            print("New cycle")
            for i in range(len(allNotices)):
                print("Notice "+str(i)+" : "+allNotices[i].Heading+" with TTL: "+str(allNotices[i].ttl))
                if(allNotices[i].ttl != 0):
                    print("Updating board")
                    _update(allNotices[i]) 
                    allNotices[i].ttl = allNotices[i].ttl - 1    
                    time.sleep(8)
            
                    
                                
            
def _update(notice):
    global BottomMain
    
    BottomMain.grid_forget()
    BottomMain = tk.Frame(root , width=1350 , height=650 , bd=12, padx=10 , bg='white')    
    BottomMain.grid(row=1,column=0)
    if(notice.Heading != ""):
        lblHeading = Label(BottomMain,font=('Arial Black',30,'bold'), text=notice.Heading ,padx=20, width=45, height=2)
        lblHeading.grid(row=0,column=0)
    if(notice.contestImg!="" and notice.Msg !=""):
        Body = tk.Frame(BottomMain, width=1350, bg="white")
        Body.grid(row=1, column=0)
        lblMsg = Label(Body,font=('',25,'bold'),bg='white', padx=5, width=30, height=11, justify='center', wraplength=1300, text=notice.Msg)
        lblMsg.grid(row=0,column=0)
        img1 = Image.open("C:/Users/Kenneth/Desktop/" +notice.contestImg+".png")
        img2 = img1.resize((720, 360),Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img2)
        lblImg = Label(Body, image=img, width=720, height=360, bg="white")
        lblImg.image=img
        lblImg.grid(row=0,column=1)
    elif(notice.Msg != "" ):
        lblMsg = Label(BottomMain,font=('',25,'bold'),bg='white', padx=5, width=65, height=11, justify='center', wraplength=1300, text=notice.Msg)
        lblMsg.grid(row=1,column=0)
        
    Footer = tk.Frame(BottomMain, width=1350, height=100)
    Footer.grid(row=2,column=0)

    if(notice.Publisher != ""):
        lblPublisher = Label(Footer,font=(15), bg="white", text="Published By: "+notice.Publisher , width=33)
        lblPublisher.grid(row=0,column=0)
    if(notice.Addressee!=""):
        lblAddressee = Label(Footer,font=(15), bg="white", text="To: "+notice.Addressee , width=33)
        lblAddressee.grid(row=0,column=1)
        
    lblDate = Label(Footer, font=(15),bg='white', text=notice.publishDate, width=33)
    lblDate.grid(row=0, column=2)
        

# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))

def on_message(client, obj, msg):
    print(str(msg.payload) )
    if(str(msg.payload) ):
        
        contestImg = ""
        Heading = ""
        Msg = ""
        Publisher = ""
        Addressee = ""
        
        noticeReceived = str(msg.payload)
        addnoticeDB(noticeReceived)
        result = re.search('%1(.*)%2(.*)%3(.*)%4(.*)%5(.*)%6', noticeReceived)
        print(result)
        temp = result.group(1)
        if(temp):
            print("Temp: "+temp)
            path = "C:/Users/Kenneth/Desktop/" +temp+".png"
            gdd.download_file_from_google_drive(file_id = temp, dest_path= path)
        else:
            print('temp var')
        contestImg = result.group(1)
        Heading = result.group(2)
        Msg = result.group(3)
        Publisher = result.group(4)
        Addressee = result.group(5)
        newNotice(contestImg, Heading, Msg, Publisher, Addressee)
        
def on_publish(client, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print(string)



def start_nb():
    mqttc = mqtt.Client()
    # Assign event callbacks
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
 
    topic = 'notice'
 
    # Connect
    mqttc.username_pw_set("hnycoagi", "9s5emAWkWu8G")
    mqttc.connect("soldier.cloudmqtt.com", 14040)
 
    # Start subscribe, with QoS level 0
    mqttc.subscribe(topic, 0)
    print("Connection to MQTT opened")
    rc = 0
    while rc == 0:
        rc = mqttc.loop()
    print("rc: " + str(rc)+" Connection to MQTT closed")
    start_nb()
    
def addnoticeDB(noticeReceived):
    try:
        sqliteConnection = sqlite3.connect('notices.db',
                                           detect_types=sqlite3.PARSE_DECLTYPES |
                                           sqlite3.PARSE_COLNAMES)
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        
        
        sqlite_create_table_query = '''CREATE TABLE if not exists notices (
                                       hding TEXT,
                                       msg TEXT ,
                                       img TEXT ,
                                       pub TEXT ,
                                       addresse TEXT,
                                       noticeDate timestamp);'''

        cursor = sqliteConnection.cursor()
        cursor.execute(sqlite_create_table_query)
        #run above string only once~nathan
        
        sqlite_insert_with_param = """INSERT INTO 'notices'
                          ('hding', 'msg', 'img', 'pub', 'addresse', 'noticeDate') 
                          VALUES (?, ?, ?,?, ?, ?);"""
        
        result = re.search('%1(.*)%2(.*)%3(.*)%4(.*)%5(.*)%6', noticeReceived)
        data_tuple = (result.group(1), result.group(2), result.group(3), result.group(4), result.group(5),datetime.datetime.now(),)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        
        sqliteConnection.commit()
        print("Notice added successfully \n")
        startDate =datetime.datetime(2014, 1, 1) #configure in GUI
        endDate =datetime.datetime(2020, 1, 1) #configure in GUI
        sqlite_select_query = """SELECT noticeDate from notices where noticeDate > ? and noticeDate < ?"""
        cursor.execute(sqlite_select_query,(startDate, endDate,))
        records = cursor.fetchall()
        for row in records:
            print(row)

        cursor.close()


    except sqlite3.Error as error:
        print("SQLite Error", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("SQLite connection is closed")


root=Tk()
root.title("Project")
root.geometry("1350x700+0+0")
Tops = tk.Frame (root , width=1350 , height=100 , bd=12 , relief="raise" , bg='black')
Tops.grid(row=0,column=0)
lbTitle=Label(Tops , font=('Times New Roman' , 40 , 'bold') ,width=42, text='Notice Board - Fr. CRCE', bg='black' , fg='gold')
lbTitle.grid(row=0,column=0)
BottomMain = tk.Frame(root , width=1350 , height=650 , bd=12, padx=10 , bg='white')    
BottomMain.grid(row=1,column=0)
lblHeading = Label(BottomMain,font=('Arial Black',30,'bold'), text="No notice to show yet",padx=20, width=45, height=2)
lblHeading.grid(row=0,column=0)
lblMsg = Label(BottomMain ,font=('',25,'bold'),bg='white', padx=5, width=65, height=11, justify='center', wraplength=1300, text="")
lblMsg.grid(row=1,column=0)
Footer = tk.Frame(BottomMain, width=1350, height=100)
Footer.grid(row=2,column=0)
lblPublisher = Label(Footer,font=(15), bg="white", text="Published By:", width=50)
lblPublisher.grid(row=0,column=0)
lblAddressee = Label(Footer,font=(15), bg="white", text="To:", width=50)
lblAddressee.grid(row=0,column=1)

btnStart = Button(root, width=1,height=1, command=Thread(target=start_nb).start())
btnStart.grid(row=4,column=20)
btnStart2 = Button(root, width=1,height=1, command=Thread(target=carousel).start())
btnStart2.grid(row=4,column=21)

root.mainloop()
