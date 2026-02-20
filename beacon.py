from microbit import *
import radio

radio.on()
radio.config(group=2)
radio.config(power=1)

while True:
    display.show("T")
    msg = b"$TFR_[radius in m]_[ddmm.mmmm]_[N/S]_[dddmm.mmmm]_[E/W]*"
    radio.send(msg)
