import be_jogio
import jogio_cmd_motors
import time, socket
mysock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server = "127.0.0.1"
port = 55142
msgout = "CLIENT DISPONIBLE"

def setHeadingSimple(head):
    headOk = False
    jogio_cmd_motors.motorInit()
    jogio_cmd_motors.motorRightForward()
    jogio_cmd_motors.motorLeftBackward()
    jogio_cmd_motors.motorsSetSpeed(25, 25)
    
    while (not headOk):
        headMes = be_jogio.compassHighRes()
        headErr = head - headMes
        if (abs(headErr) < 5):
            headOk = True
            jogio_cmd_motors.motorsSetSpeed(0, 0)
        else :
            print headErr
            time.sleep(0.1)

def setHeading(head):
    headOk = False
    jogio_cmd_motors.motorsSetSpeed(25, 25)
    
    while (not headOk) :
        headMes = be_jogio.compassHighRes()
        headErr = head - headMes
        headErr = headErr % 360
        if headErr > 180 :
            headErr = headErr - 360
        elif headErr < 180 :
            headErr = headErr + 360
        if headErr >= 0 :
            jogio_cmd_motors.motorLeftForward()
            jogio_cmd_motors.motorRightBackward()
        else :
            jogio_cmd_motors.motorRightForward()
            jogio_cmd_motors.motorLeftBackward()
            jogio_cmd_motors.motorsSetSpeed(25, 25)
        if (abs(headErr) < 5):
            headOk = True
            jogio_cmd_motors.motorsSetSpeed(0, 0)
        else :
            time.sleep(0.1)
            
            
def setHeadingProp(head, alpha):
    headOk = False
    jogio_cmd_motors.motorsSetSpeed(25, 25)
    
    while (not headOk) :
        headMes = be_jogio.compassHighRes()
        headErr = head - headMes
        headErr = headErr % 360
        if headErr > 180 :
            headErr = headErr - 360
        elif headErr < -180 :
            headErr = headErr + 360
        err = abs(headErr)
        if headErr >= 0 :
            jogio_cmd_motors.motorLeftForward()
            jogio_cmd_motors.motorRightBackward()
            jogio_cmd_motors.motorsSetSpeed(25 + alpha*err, 25 + alpha*err)
        else :
            jogio_cmd_motors.motorRightForward()
            jogio_cmd_motors.motorLeftBackward()
            jogio_cmd_motors.motorsSetSpeed(25 + alpha*err, 25 + alpha*err)
        if (abs(headErr) < 2):
            headOk = True
            jogio_cmd_motors.motorsSetSpeed(0, 0)
        else :
            print headErr
            time.sleep(0.1)
            

def goLineHeading (head, speed, duration):
    t = duration
    while (t>0):
        be_jogio.ledsSet(3)
        setHeading(head)
        jogio_cmd_motors.motorRightForward()
        jogio_cmd_motors.motorLeftForward()
        jogio_cmd_motors.motorsSetSpeed(speed, speed)
        be_jogio.ledsSet(12)
        time.sleep(duration/15)
        t = t - duration/15
        
def goLine(head, n) :
    setHeadingProp(head, 0.1)
    s = be_jogio.sonarSingle(3)
    s = n + 1
    while s>n :
        setHeadingProp(head, 0.1)
        jogio_cmd_motors.motorRightForward()
        jogio_cmd_motors.motorLeftForward()    
        jogio_cmd_motors.motorsSetSpeed(80, 80)
        time.sleep(0.1)
        s = be_jogio.sonarSingle(3)
    jogio_cmd_motors.motorsSetSpeed(0, 0)

def goLeft():
    jogio_cmd_motors.motorRightForward()
    jogio_cmd_motors.motorLeftBackward()
    jogio_cmd_motors.motorsSetSpeed(80, 80)
    
def goRight():
    jogio_cmd_motors.motorRightBackward()
    jogio_cmd_motors.motorLeftForward()
    jogio_cmd_motors.motorsSetSpeed(80, 80)
    
def goGo():
    while True :
        mysock.sendto(msgout, (server, port))
        msgin, rserver = mysock.recvfrom(255)
        h = be_jogio.compassHighRes()
        msg = msgin.split()
        if msg[0] == "0" :
                if msg[1] == "1" :
                        goLineHeading(h+180,1)
                elif msg[1] == "-1" :
                        goLineHeading(h,1)
        elif msg[0] == "1" :
                if msg[1] == "0" :
                        goLineHeading(h+90,1)
                if msg[1] == "1" :
                        goLineHeading(h+135,1)
                elif msg[1] == "-1" :
                        goLineHeading(h+45,1)
        elif msg[0] == "-1" :
                if msg[1] == "0" :
                        goLineHeading(h-90,1)
                if msg[1] == "1" :
                        goLineHeading(h-135,1)
                elif msg[1] == "-1" :
                        goLineHeading(h-45,1)

if __name__ == "__main__":
    be_jogio.ledsSet(15)
    goGo()
