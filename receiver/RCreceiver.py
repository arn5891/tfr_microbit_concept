from microbit import *
import nmeaparser
import cutebot
import log
import radio
import time

uart.init(baudrate=9600, tx = pin1, rx = pin2)

def bprint(s):
    uart.init(115200)
    print(str(s)+"\n")
    uart.init(baudrate=9600, tx = pin1, rx = pin2)
            
def update_loc(v):
    if uart.any():
        uart_msg = str(uart.read())
        if "GPGGA" in uart_msg:
            sntc = nmeaparser.parse(uart_msg, "GPGGA")
            if nmeaparser.BAD_MSG != sntc:
                #bprint(sntc)
                if sntc[5] != "0":
                    bprint("ok")
                    return {"lat":[sntc[1], sntc[2]],"lon":[sntc[3], sntc[4]]}
    #bprint("fail")
    return v

def update_tfr(m):
    tfr = nmeaparser.BAD_MSG
    if m is not None:
        tfrdata = nmeaparser.parse(m, "TFR")
        if tfrdata != nmeaparser.BAD_MSG:
            tfrlat = [tfrdata[1],tfrdata[2]]
            tfrlon = [tfrdata[3],tfrdata[4]]
            tfr_dd = nmeaparser.dec_deg(tfrlat,tfrlon)
            radius = tfrdata[0]
            tfr = [tfr_dd,radius]
    if tfr is not nmeaparser.BAD_MSG:
        tfr_bank.append(tfr)

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

#setup
ERRROR_MARGIN = 2.5
auton = False
start = False
starttime = 0
volt = 0
m = None
ch = 1
switchtime = 0
itvl_ch1 = 30
itvl_ch2 = 30
tfr_bank = []
uart_msg = ""
init_loc = None
while init_loc is None:
    init_loc = update_loc(init_loc)
il_dd = nmeaparser.dec_deg(init_loc["lat"],init_loc["lon"])
cur_loc = {"lat":init_loc["lat"],"lon":init_loc["lon"]}
cl_dd = nmeaparser.dec_deg(cur_loc["lat"],cur_loc["lon"])

#display listening intervals- A side for ch1(remote), B side for ch2(TX)
display.set_pixel(0,itvl_ch1//30-1,9)
display.set_pixel(4,itvl_ch2//30-1,9)

#config
radio.on()
radio.config(group = 2)
radio.config(power = 1)
radio.config(length = 100)

while True:
    cur_loc = None
    while cur_loc is None:
        cur_loc = update_loc(cur_loc)
    bprint("ok")
    cl_dd = nmeaparser.dec_deg(cur_loc["lat"],cur_loc["lon"])
    rad_msg = radio.receive()
    update_tfr(rad_msg)
    for i in tfr_bank:
        d = nmeaparser.hav_formula(i[0],cl_dd)-(ERRROR_MARGIN*2)
        log.add({"dist to tfr(+/- 2.5 m) https://forum.arduino.cc/t/accuracy-of-neo6mv2/205205/2":d})
