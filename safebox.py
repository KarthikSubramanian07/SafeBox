import serial
import pygame
import smtplib 
from threading import Timer
import sys

serialPort = serial.Serial('/dev/ttyACM0',9600)
s = [0,1]
f = 0;
userpassword = "1234";
cnt = 0
password=""
wtstr=""
wt=0
net_wt=0
correctpassword=False
iCnt=0
prev_wt=0
# Main program loop

subject=""
msg=""


def resetPassword():
    print("reset password called")
    correctPassword=False


def alarm():
    print("ALARM INIT")
    pygame.mixer.init() # Initialize PyGame
    pygame.mixer.music.load("/home/pi/Documents/alarm.mp3")
    pygame.mixer.music.play()
    print("ALARM PLAYED")

def send_email(subject, msg):
    try:
        print("email here", subject, msg)
        server = smtplib.SMTP('smtp.gmail.com:587')
        print(server)
        server.ehlo()
        server.starttls()
        server.login("s****@gmail.com", "****")
        print("email logged in")
        message = 'Subject: {}\n\n{}'.format(subject, msg)
        print(message)
        server.sendmail("s****@gmail.com", "h***@gmail.com", message)
        server.quit()
        print("Success: Email sent!")
    except:
        print("Email failed to send.")
        e = sys.exc_info()[0]
        print(e)

while(1):
    # Wait for some serial data
    if (serialPort.in_waiting > 0):
        serialString = str(serialPort.readline())
        # print(serialString)
        # Check to see if the data is a measurement reading
        stringArray = serialString.split(':')
        # print(stringArray)     
        if((len(stringArray) > 1)):
            if(cnt==4):
                cnt=0
                correctpassword=False
            print(stringArray[1])
            passwordchar = str(stringArray[1])
            passwordchar = passwordchar.replace("\\r","")
            passwordchar = passwordchar.replace("\\n'","")
            passwordchar = passwordchar.replace("k-","")
            #print("passwordchar:"+passwordchar)
            password = password + passwordchar.strip()
            cnt = cnt + 1
            if(cnt==4):
                if(password==userpassword):
                    print("correct")
                    correctpassword=True
                    t = Timer(30.0, resetPassword)
                    t.start() # after 30 seconds, reset the password
                    print("STARTED RESET PASSWORD")
                else:
                    print("wrong password:"+password)
                    password=""
                    correctpassword=False
        else:
            wtstr = str(stringArray[0])
            wtstr = wtstr.replace("b'","")
            wtstr = wtstr.replace("\\r","")
            wtstr = wtstr.replace("\\n'","")
            wtstr = wtstr.replace("-","")
            wtstr = wtstr.strip()
            try:
                wt=float(wtstr)
                wt=round(wt)
                print("wt,prev,iCnt:",wt,prev_wt,iCnt)
                if(wt != net_wt and iCnt<5):
                    if(wt != prev_wt):
                        print("wait for stable weight:",wt,prev_wt)
                        prev_wt=wt
                        continue
                    else:
                        # increment the count for stable weight
                        iCnt=iCnt+1
                        prev_wt=wt
                        continue
                else:
                    print("Stable weight",wt)
                    iCnt=0
                    prev_wt=wt
                         


                    
                
                
                print("wt,net:",wt,net_wt)
                if(abs(net_wt-wt)<2):
                    # do not do anything if diff is less than 2 oz
                    continue
                if(net_wt==0):
                    net_wt=wt
                    if(wt>0):
                        subject = "SafeBox Notification: You've received new  package(s)"
                        msg = "You have received the package(s) in the SafeBox. Current weight on the SafeBox: " + str(wt) + " oz"
                        send_email(subject, msg)                        
                        print("SEND MAIL: New Package Received")
                elif(wt > net_wt):
                    net_wt=wt
                    subject = "SafeBox Notification: You've received new  package(s)"
                    msg = "You have received the package(s) in the SafeBox. Current weight on the SafeBox: " + str(wt) + " oz"
                    send_email(subject, msg)                        
                    print("SEND MAIL: New Package Received")
                elif(wt == net_wt):
                    print("package at box")
                else:
                    if(correctpassword):
                        subject = "SafeBox Notification: You've taken the package(s)"
                        msg = "You have taken the package(s) from the SafeBox. Current weight on the SafeBox: " + str(wt) + " oz"
                        send_email(subject, msg)                        
                        print("SEND MAIL: User has taken package")
                        net_wt=wt
                    else:
                        print("THEFT!!!!THEFT!!!!THEFT!!!")
                        alarm()
                        subject = "SafeBox ALERT: Your package(s) have been taken without password"
                        msg = "One or more package(s) are taken from the SafeBox without entering password. Current weight on the SafeBox: " + str(wt) + " oz"
                        send_email(subject, msg)                        
                        print("new,net wt:",wt, net_wt)
                        net_wt=wt
                
                
            except ValueError:    
                print("except wtstr:"+wtstr)
            
def send_email(subject, msg):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login("s****@gmail.com", "****")
        message = 'Subject: {}\n\n{}'.format(subject, msg)
        server.sendmail("s****@gmail.com", "h****@gmail.com", message)
        server.quit()
        print("Email sent:", subject)
    except:
        print("Email failed:", subject)
        e = sys.exc_info()[0]
        print(e)                    
                    
                    
                
