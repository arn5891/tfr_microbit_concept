from microbit import *
import radio

radio.on()
radio.config(group=1)
radio.config(power=1)

while True:
    display.show("T")
    msg = "0"
    radio.send(msg)