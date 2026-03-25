from microbit import *
import radio

radio.on()
radio.config(data_rate = radio.RATE_2MBIT)
radio.config(channel=40)
radio.config(length=100)

while True:
    display.show("T")
    msg = '$TFR,[radius],[ddmm.mmmm],[N/S],[dddmm.mmmm],[E/W]*'
    radio.send(msg)
