from microbit import *
import log
def parse(b,_id):
    b = str(b)
    b = b[b.find("$"+_id+",")+len("$"+_id+","):]
    return b[:b.find("*")+1] if (b.find("*") != -1) else b
print("start")
uart.init(baudrate=9600, tx = pin19, rx = pin20)
msg = ""
while(True):
    if uart.any():
        msg = str(uart.read())
        if "GPGGA" in msg:
            uart.init(115200)
            print(parse(msg, "GPGGA"))
            #log.add({"test":msg})
            uart.init(baudrate=9600, tx = pin19, rx = pin20)
    sleep(100)
