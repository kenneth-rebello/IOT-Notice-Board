import tkinter as tk
from tkinter import messagebox
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from PIL import ImageTk, Image
import paho.mqtt.client as mqtt
from threading import Thread
from google_drive_downloader import GoogleDriveDownloader as gdd
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import smtplib
import imghdr
from email.message import EmailMessage


txtHeading = ''
txtMsg = ''
txtImg = ''
txtPublisher =''
txtAddressee = ''
txtEmail:''
mqttc = mqtt.Client()


def send_mail():
    global txtEmail, txtMsg, txtImg, img
    print('insider mail function')
    msg=EmailMessage()
    s=txtHeading
    print(s)
    msg['Subject']=s
    msg['From']='banquecosmopolite@gmail.com'
    msg['To']=txtEmail
    body="Notice published: "+txtMsg+'\n'
    print(body)
    msg.set_content(body)
    if(txtImg != ""):
        print('now adding image')
        with open(img,'rb') as f:
            file_data=f.read()
            file_type=imghdr.what(f.name)
            file_name='notice'
        msg.add_attachment(file_data,maintype='image',subtype=file_type,filename=file_name)
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        smtp.login('banquecosmopolite@gmail.com','chhaganlal123*')
        smtp.send_message(msg)


def start_nb():
    global mqttc
    # Assign event callbacks
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    
    topic = 'notice'
    
    # Connect
    mqttc.username_pw_set("hnycoagi", "9s5emAWkWu8G")
    mqttc.connect("soldier.cloudmqtt.com",14040)
    
    # Start subscribe, with QoS level 0
    mqttc.subscribe(topic, 0)
    
    rc = 0
    while rc == 0:
        rc = mqttc.loop()
    print("rc: " + str(rc))
    
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))

def on_publish(client, obj, mid):
    print("mid: " + str(mid))
    send_mail()


    
def publish():
    global mqttc,entMsg, entHeading, entImg, entPublisher, entAddressee, entEmail, txtMsg, txtHeading, txtImg,img, txtPublisher, txtAddressee, txtEmail
    topic = 'notice'
    txtHeading = entHeading.get('1.0','end-1c')
    txtMsg = entMsg.get('1.0','end-1c')
    txtImg = entImg.get('1.0','end-1c')
    img=txtImg
    
    txtPublisher = entPublisher.get('1.0','end-1c')
    txtAddressee = entAddressee.get('1.0','end-1c')
    txtEmail = entEmail.get('1.0','end-1c')
    Publisher = txtPublisher
    Addressee = txtAddressee
    if(txtImg != ''):
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile('my_cred.txt')
        drive = GoogleDrive(gauth)
        path = ''
        path=txtImg.replace('\\','/')
        if(path != ''):
            file1 = drive.CreateFile()
            file1.SetContentFile(path)
            file1.Upload()
            permission = file1.InsertPermission({
                                    'type': 'anyone',
                                    'value': 'anyone',
                                    'role': 'reader'})
        
        txtImg = (file1['alternateLink'])
        temp = txtImg.partition('file/d/');
        temp2 = temp[2].partition('/view?');
        txtImg = temp2[0]
    noticeText = "%1"+txtImg+"%2"+txtHeading+"%3"+txtMsg+"%4"+txtPublisher+"%5"+txtAddressee+"%6"
    # Publish a message
    print('publishing')
    mqttc.publish(topic, noticeText)
    entHeading.delete('1.0', END)
    entMsg.delete('1.0', END)
    entImg.delete('1.0', END)
    entPublisher.delete('1.0', END)
    entAddressee.delete('1.0', END)
    entEmail.delete('1.0', END)
    
    
def AddImage():
    global root, newFile, entImg
    root.fileName = filedialog.askopenfilename(filetypes = ( [("All files","*.*")]))
    newFile = root.fileName
    entImg.insert(END, newFile)
    

def focus_next_window(event):
    event.widget.tk_focusNext().focus()
    return("break")
    
root=Tk()
root.title("Project")
root.geometry("1300x650+0+0")
newFile =''

    
Tops = tk.Frame (root , width=1350 , height=100 , bd=12 , relief="raise" , bg='black')
Tops.grid(row=0,column=0, columnspan=4)
lbTitle=Label(Tops , font=('Times New Roman' , 40 , 'bold') ,width=42, text='Notice Board - Fr. CRCE', bg='black' , fg='gold')
lbTitle.grid(row=0,column=0)


lblHeading = Label(root, text='Heading: ', width=7, font=('',25,''))
lblHeading.grid(row=1,column=0, padx=2, pady=10)
entHeading = Text(root, width=55, height=1, font=('',20,''))
entHeading.grid(row=1,column=1, padx=5, pady=10, columnspan=3)
entHeading.bind("<Tab>", focus_next_window)
lblMsg = Label(root, text='Message: ', width=10, font=('',25,''))
lblMsg.grid(row=2,column=0 ,padx=2, pady=10)
entMsg = Text(root , width=75, height=5, font=('',15,''))
entMsg.grid(row=2,column=1, padx=5, pady=10, columnspan=3)
entMsg.bind("<Tab>", focus_next_window)

lblImg = Label(root, text='Image: ', width=10, font=('',25,''))
lblImg.grid(row=3,column=0, padx=2, pady=10)
entImg = Text(root , width=50, height=1, font=('',15,''))
entImg.grid(row=3,column=1, padx=5, pady=10)
entImg.bind("<Tab>", focus_next_window)
btnImg = Button(root, text='Add Image', command=AddImage, font=(15), bg='black', fg='white')
btnImg.grid(row=3, column=2)


lblPub = Label(root, text='Publisher: ', width=10, font=('',25,''))
lblPub.grid(row=4,column=0, padx=2, pady=10)
entPublisher = Text(root , width=75, height=1, font=('',15,''))
entPublisher.grid(row=4,column=1, padx=5, pady=10, columnspan=3)
entPublisher.bind("<Tab>", focus_next_window)
lblAdd = Label(root, text='Addressee: ', width=10, font=('',25,''))
lblAdd.grid(row=5,column=0, padx=2, pady=10)
entAddressee = Text(root , width=75, height=1, font=('',15,''))
entAddressee.grid(row=5,column=1, padx=5, pady=10, columnspan=3)
entAddressee.bind("<Tab>", focus_next_window)

lblEmail = Label(root, text='Your Email: ', width=10, font=('',25,''))
lblEmail.grid(row=6,column=0 ,padx=2, pady=10)
entEmail = Text(root , width=75, height=1, font=('',15,''))
entEmail.grid(row=6,column=1, padx=5, pady=10, columnspan=3)
entEmail.bind("<Tab>", focus_next_window)

btnPublish = Button(root, width=10,text='PUBLISH',font=(30), command=publish, bg='green', fg='white')
btnPublish.grid(row=7, column=0, columnspan=4)

btnStart = Button(root, width=1,height=1, command=Thread(target=start_nb).start())
btnStart.grid(row=6,column=10)

root.mainloop()
