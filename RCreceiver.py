from microbit import *
import radio
from cutebot import *
from time import *

v = 0
ch = 1
itvl = 90#30 to 90 ms w 30 ms intervals
switchtime = ticks_add(ticks_ms(), itvl)
auto = False
radio.config(group=ch)
radio.on()
radio.config(power=1)
while True:
    if ch == 1:
        m = radio.receive()
        display.show(str(m), delay=0, wait=False)
        if m is not None:
            v = int(str(m))*25
        else:
            v = 0
        if ticks_ms() >= switchtime:
            switchtime = ticks_add(ticks_ms(), itvl)
            ch = 2
            radio.config(group=ch)
    elif ch == 2:
        m = radio.receive()
        display.show(str(m), delay=0, wait=False)
        if m is not None:
            auto = False
        if not auto:
            if ticks_ms() >= switchtime:
                switchtime = ticks_add(ticks_ms(), itvl)
                ch = 1
                radio.config(group=ch)
        #else:
        #    v = 0
    set_motors_speed(v,v)