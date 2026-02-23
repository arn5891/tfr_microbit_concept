from microbit import *
import nmeaparser
import cutebot
import log
import radio
import time

uart.init(baudrate=9600, tx = pin1, rx = pin2)

def bprint(s):
    uart.init(115200)
    print(s)
    uart.init(baudrate=9600, tx = pin1, rx = pin2)
            
def update_loc(v):
    if uart.any():
        uart_msg = uart.read()
        if "GPGGA" in str(uart_msg):
            sntc = nmeaparser.parse(uart_msg, "GPGGA")
            if sntc is not None:
                return {"lat":[sntc[1], sntc[2]],"lon":[sntc[3], sntc[4]]}
    return v

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
auton = False
start = False
starttime = 0
volt = 0
m = None
ch = 1
switchtime = 0
itvl_ch1 = 30
itvl_ch2 = 30
tfr_bank = {}
uart_msg = ""
init_loc = None

while init_loc is None:
    init_loc = update_loc(init_loc)
#bprint("run1")
#bprint(init_loc["lat"])
il_dd = nmeaparser.dec_deg(init_loc["lat"],init_loc["lon"])
#bprint("end1")
cur_loc = {"lat":init_loc["lat"],"lon":init_loc["lon"]}
cl_dd = None

#display listening intervals- A side for ch1(remote), B side for ch2(TX)
display.set_pixel(0,itvl_ch1//30-1,9)
display.set_pixel(4,itvl_ch2//30-1,9)

#config
radio.on()
radio.config(group = 1)
radio.config(power = 1)
radio.config(length = 100)


while(True):
    #set intervals
    if release(button_a):
        itvl_ch1= itvl_ch1+30 if itvl_ch1 < 90 else 30
        display.clear()
        display.set_pixel(0,itvl_ch1//30-1,9)
        display.set_pixel(4,itvl_ch2//30-1,9)
    if release(button_b):
        itvl_ch2= itvl_ch2+30 if itvl_ch2 < 90 else 30
        display.clear()
        display.set_pixel(0,itvl_ch1//30-1,9)
        display.set_pixel(4,itvl_ch2//30-1,9)
    
    cur_loc = update_loc(cur_loc)
    #bprint("run2")
    if cur_loc is not None:
        cl_dd = nmeaparser.dec_deg(cur_loc["lat"],cur_loc["lon"])
    #bprint("end2")
    
    m = radio.receive()
    
    if start is not True and m is not None:
        display.show("R")
        log.add({"intervals(ms, 1-2)":str(itvl_ch1)+","+str(itvl_ch2)})
        switchtime = time.ticks_add(time.ticks_ms(),itvl_ch1)
        start = True
        starttime = time.ticks_ms()
        
    if start:
        if ch == 1:
            if auton is not True:
                if m == "1":
                    volt = 80
                elif m == "0":
                    bprint("other msg")
                    volt = 0
            else:
                bprint("auton engaged")
                volt = 0
        elif ch == 2:
            #bprint(m)
            if m is not None:
                tfrdata = nmeaparser.parse(m,"TFR")
                bprint(tfrdata)
                #$TFR_[radius in m]_[ddmm.mmmm]_[N/S]_[dddmm.mmmm]_[E/W]*[no checksum]
                if tfrdata is not None:
                    tfrlat = (tfrdata[1],tfrdata[2])
                    tfrlon = (tfrdata[3],tfrdata[4])
                    #bprint("run3")
                    tfr_dd = nmeaparser.dec_deg(tfrlat,tfrlon)
                    #bprint(tfr_dd)
                    tfr = {"_".join([str(tfr_dd[0]),str(tfr_dd[1])]):tfrdata[0]}
                    if len(tfr_bank)==0:
                        log.add({"Time to first packet(ms)":time.ticks_ms()-starttime})
                        tfr_bank.update(tfr)
            for (i, j) in tfr_bank.items():
                i_dd = i.split("_")
                i_dd[0] = float(i[0])
                i_dd[1] = float(i[1])
                d = nmeaparser.hav_formula(cl_dd,i_dd)
                display.show(str(cl_dd[0])[-1])
                log.add({"dist from TFR(m)":d})
                if d < j+1:
                    bprint("uh oh")
                    auton = True
                    log.add({"Time triggered(ms)":time.ticks_ms()-starttime})
                    log.add({"Distance traveled when triggered(m)":nmeaparser.hav_formula(cl_dd,il_dd)})
                    log.add({"Distance from TFR when triggered(m)":d})
                    log.add({"Avoidance success":nmeaparser.hav_formula(cl_dd,il_dd) > d})
        
        if time.ticks_ms() >= switchtime:
            ch = 2 if ch == 1 else 1
            radio.config(channel=ch)
            switchtime = time.ticks_add(time.ticks_ms(),[itvl_ch1,itvl_ch2][ch-1])
        cutebot.set_motors_speed(volt,volt)
