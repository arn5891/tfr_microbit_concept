from microbit import *
import radio
from cutebot import *
from time import *

v = 0
ch2 = False
itvl = 1000#30 to 90 ms w 30 ms intervals
switchtime = ticks_add(ticks_ms(), itvl)
auto = False
radio.config(group=(int(ch2)+1))
radio.on()
radio.config(power=1)
while True:
    m = ""
    m = radio.receive()
    display.show(str(m), delay=0, wait=False)
    if m is not None:
        v = int(str(m))*25
    elif ch2 == False:
        v = 0
    if ticks_ms() >= switchtime:
        switchtime = ticks_add(ticks_ms(), itvl)
        ch2 = not ch2
        radio.config(group=(int(ch2)+1))
    set_motors_speed(v,v)
