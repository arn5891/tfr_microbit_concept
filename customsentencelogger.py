from microbit import *
import nmeaparser
import log

uart.init(baudrate=9600, tx = pin1, rx = pin2)
cmds = [
b'\xB5\x62\x06\x01\x08\x00\xF0\x01\x00\x00\x00\x00\x00\x00\x00\x28', # GLL off
b'\xB5\x62\x06\x01\x08\x00\xF0\x02\x00\x00\x00\x00\x00\x00\x01\x2F', # GSA off
b'\xB5\x62\x06\x01\x08\x00\xF0\x03\x00\x00\x00\x00\x00\x00\x02\x36', # GSV off
b'\xB5\x62\x06\x01\x08\x00\xF0\x04\x00\x00\x00\x00\x00\x00\x03\x3D', # RMC off
b'\xB5\x62\x06\x01\x08\x00\xF0\x05\x00\x00\x00\x00\x00\x00\x04\x44', # VTG off
b'\xB5\x62\x06\x01\x08\x00\xF0\x41\x00\x00\x00\x00\x00\x00\x40\x6D', # TXT off
b'\xB5\x62\x06\x01\x08\x00\xF0\x00\x01\x00\x00\x00\x00\x00\x00\x24'  # GGA on
]
for c in cmds:
    uart.write(c)
set_rate_5hz = b'\xB5\x62\x06\x08\x06\x00\xC8\x00\x01\x00\x01\x00\xDE\x6A'
uart.write(set_rate_5hz)

def bprint(s):
    uart.init(115200)
    print(str(s)+"\n")
    uart.init(baudrate=9600, tx = pin1, rx = pin2)

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
    
def update_loc(v):
    if uart.any():
        uart_msg = str(uart.read())
        if "GPGGA" in uart_msg:
            log.add({".":uart_msg})
            sntc = nmeaparser.parse(uart_msg, "GPGGA")
            bprint(sntc)
            if nmeaparser.BAD_MSG != sntc:
                if sntc[5] != "0":
                    return "$TFR"+",1,"+",".join(sntc[1:5])+"*"
    return v

#setup
auton = False
start = False
volt = 0
m = None
ch = 1
switchtime = 0
itvl_ch1 = 30
itvl_ch2 = 30
tfr_bank = {}
uart_msg = ""
init_loc = None

#config

count = 0
while(True):
    if release(button_a):
        display.clear()
        c_loc = None
        while c_loc is None:
            c_loc = update_loc(c_loc)
        log.add({"custom NMEA":str(c_loc)})
        display.show(Image.DIAMOND)
        count+=1
