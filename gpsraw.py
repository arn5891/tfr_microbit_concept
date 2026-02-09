from microbit import *
import log

uart.init(baudrate=9600, tx = pin19, rx = pin20)

states = {}

def release(obj):
    if obj == button_a:
        t = "a"
    else:
        t = "b"
    r = False
    if t not in states:
        states[t] = obj.is_pressed()
    if states[t] != obj.is_pressed() and obj.is_pressed() == False:
        r = True
    states[t] = obj.is_pressed()
    return r
    
msg = ""
while(True):
    if uart.any():
        msg = str(uart.read())
    if release(button_a):
        log.add({"test":msg})
