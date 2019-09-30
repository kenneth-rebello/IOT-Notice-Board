import tkinter as tk
from tkinter import messagebox
from tkinter import *
from PIL import ImageTk, Image
import paho.mqtt.client as mqtt
from threading import Thread
from google_drive_downloader import GoogleDriveDownloader as gdd
import re
import os
import time

allNotices = []

class Notice:
    def __init__(self,i, h, m, p, a):
        self.Heading = h
        self.Msg = m
        self.Publisher = p
        self.Addressee = a
        self.contestImg = i
        
    
def newNotice(contestImg, Heading, Msg, Publisher, Addressee):
    global allNotices
    
    print('making notice object')
    notice = Notice(contestImg,Heading, Msg, Publisher, Addressee)
    print(notice.Heading)
    allNotices.append(notice)
    print(allNotices)
    
def carousel():
    global allNotices
    
    while 1:
        if(len(allNotices)>0):
            
            for i in range(len(allNotices)):
                _update(allNotices[i]) 
                time.sleep(5)
            
            
def _update(notice):
    global BottomMain
    
    BottomMain.grid_forget()
    BottomMain = tk.Frame(root , width=1350 , height=650 , bd=12, padx=10 , bg='white')    
    BottomMain.grid(row=1,column=0)
    if(notice.Heading != ""):
        lblHeading = Label(BottomMain,font=('Arial Black',30,'bold'), text=notice.Heading ,padx=20, width=45, height=2)
        lblHeading.grid(row=0,column=0)
    if(notice.contestImg!=""):
        Body = tk.Frame(BottomMain, width=1350, bg="white")
        Body.grid(row=1, column=0)
        lblMsg = Label(Body,font=('',25,'bold'),bg='white', padx=5, width=30, height=11, justify='center', wraplength=1300, text="")
        lblMsg.grid(row=0,column=0)
        img1 = Image.open("C:/Users/Kenneth Rebello/Desktop/" +notice.contestImg+".png")
        img2 = img1.resize((720, 360),Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img2)
        lblImg = Label(Body, image=img, width=720, height=360, bg="white")
        lblImg.image=img
        lblImg.grid(row=0,column=1)
    elif(notice.Msg != "" and notice.contestImg==""):
        lblMsg = Label(BottomMain,font=('',25,'bold'),bg='white', padx=5, width=65, height=11, justify='center', wraplength=1300, text=notice.Msg)
        lblMsg.grid(row=1,column=0)
        
    Footer = tk.Frame(BottomMain, width=1350, height=100)
    Footer.grid(row=2,column=0)

    if(notice.Publisher != ""):
        lblPublisher = Label(Footer,font=(15), bg="white", text="Published By: "+notice.Publisher , width=50)
        lblPublisher.grid(row=0,column=0)
    if(notice.Addressee!=""):
        lblAddressee = Label(Footer,font=(15), bg="white", text="To: "+notice.Addressee , width=50)
        lblAddressee.grid(row=0,column=1)
        

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
        result = re.search('%1(.*)%2(.*)%3(.*)%4(.*)%5(.*)%6', noticeReceived)

        temp = result.group(1)
        path = "C:/Users/Kenneth Rebello/Desktop/" +temp+".png"
        gdd.download_file_from_google_drive(file_id = temp,
                                            dest_path= path)
        
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
    rc = 0
    while rc == 0:
        rc = mqttc.loop()
    print("rc: " + str(rc))


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
btnStart.grid(row=4,column=2)
btnStart2 = Button(root, width=1,height=1, command=Thread(target=carousel).start())
btnStart2.grid(row=4,column=1)

root.mainloop()