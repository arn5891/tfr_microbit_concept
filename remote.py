from microbit import *
import radio

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
    
radio.on()
radio.config(group=1)
radio.config(power=1)
radio.config(group=1)
go = False
stp = False

while True:
    if release(button_a):
        go = not go
    if release(button_b):
        stp = not stp    
    if stp:
        radio.send(b'0')
        display.show('0')
    elif go:
        radio.send(b'1')
        display.show('1')
    else:
        display.clear()
