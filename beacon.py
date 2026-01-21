from microbit import *
import radio

radio.on()
radio.config(group=2)
radio.config(power=1)

while True:
    display.show("T")
    msg = "T"
    radio.send(msg)
