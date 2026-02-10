from microbit import *
import log

uart.init(baudrate=9600, tx = pin19, rx = pin20)
    
msg = ""
while(True):
    if uart.any():
        msg = str(uart.read())
    log.add({"test":msg})
    display.show(msg)
