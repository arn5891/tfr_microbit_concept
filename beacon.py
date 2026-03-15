from microbit import *
import radio

radio.on()
radio.config(data_rate = radio.RATE_2MBIT)
radio.config(channel=40)
radio.config(length=100)

while True:
    display.show("T")
    msg = '$TFR,1,3358.29715,N,08411.84840,W*'
    radio.send(msg)
