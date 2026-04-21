from microbit import *
import radio

radio.on()
radio.config(data_rate = radio.RATE_2MBIT, channel = 40, length = 100, power = 7)
while True:
    display.show("T")
    msg = '$TFR,[radius],[latititude],[N/S],[longitude],[W/E]*'
    radio.send(msg)
