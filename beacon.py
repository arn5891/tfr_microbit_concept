from microbit import *
import radio

radio.on()
radio.config(group=2)
radio.config(power=1)

while True:
    display.show("T")
    msg = b'$TFR,[tfr radius in m],[ddmm.mmmm],[N/S],[dddmm.mmmm],[E/W]*'
    radio.send_bytes(msg)
