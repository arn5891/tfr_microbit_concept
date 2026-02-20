from microbit import *
import radio
from cutebot import *
from time import *

v = 0
ch2 = False
itvl = 1000#30 to 90 ms w 30 ms intervals
switchtime = ticks_add(ticks_ms(), itvl)
auton = False
pmsg = ""
radio.config(group=(int(ch2)+1))
radio.on()
radio.config(power=1)
while True:
    m = radio.receive()
    display.show(str(m), delay=0, wait=False)
    if m is not None:
        if ch2 is False:
            v = int(str(m))*25
        elif ch2 is True and str(m) == "T":
            auton = True
            v = 0
    
    elif ch2 is False:
        v = 0
    
    if ticks_ms() >= switchtime and auton is False:
        switchtime = ticks_add(ticks_ms(), itvl)
        ch2 = not ch2
        pmsg = str(m)
        radio.config(group=(int(ch2)+1))
    set_motors_speed(v,v)
