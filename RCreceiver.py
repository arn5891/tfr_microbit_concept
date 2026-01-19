from microbit import *
import radio
from cutebot import *

radio.on()
radio.config(group=1)
radio.config(power=1)
d = False
while True:
    m = str(radio.receive())
    if m == "1":
        d = True
    elif m == "0":
        d = False
    display.show(m)
    if d:
        set_motors_speed(100,100)
    else:
        set_motors_speed(0,0)