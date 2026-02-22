from microbit import *
import nmeaparser
import cutebot
import log
import radio
import time

uart.init(baudrate=9600, tx = pin1, rx = pin2)
    
def update_loc(v):
    if uart.any():
        uart.init(115200)
        uart.init(baudrate=9600, tx = pin1, rx = pin2)
        uart_msg = str(uart.read())
        if "GPGGA" in uart_msg:
            sntc = nmeaparser.parse(uart_msg, "GPGGA")
            uart.init(115200)
            print(uart_msg)
            uart.init(baudrate=9600, tx = pin1, rx = pin2)
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
cur_loc = {"lat":init_loc["lat"],"lon":init_loc["lon"]}
cl_dd = None

#display listening intervals- A side for ch1(remote), B side for ch2(TX)
display.set_pixel(0,itvl_ch1//30-1,9)
display.set_pixel(4,itvl_ch2//30-1,9)

#config
radio.on()
radio.config(group = ch)
radio.config(power = 1)


while(auton is not True):
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
    cl_dd = nmeaparser.dec_deg(cur_loc["lat"],cur_loc["lon"])
    
    m = radio.receive_bytes()
    
    if ch == 1:
        if not start and m == b'1':
            switchtime = time.ticks_add(time.ticks_ms(),itvl_ch1)
            log.add({"intervals(ms, 1-2)":str(itvl_ch1)+","+str(itvl_ch2)})
            display.show("1")
            start = True
        else:
            if auton is True or m == b'0':
                volt = 0
            elif m == b'1':
                volt = 80
        if time.ticks_ms() >= switchtime:
            display.show("2")
            ch = 2
            radio.config(group = ch)
            switchtime = time.ticks_add(time.ticks_ms(),itvl_ch2)
            
    elif ch == 2:
        if m is not None:
            tfrdata = nmeaparser.parse(m,"TFR")
            log.add({"tfr hit":str(tfrdata)})
            #$TFR_[radius in m]_[ddmm.mmmm]_[N/S]_[dddmm.mmmm]_[E/W]*[no checksum]
            if tfrdata is not None:
                tfrlat = (tfrdata[1],tfrdata[2])
                tfrlon = (tfrdata[3],tfrdata[4])
                tfr = {(tfrlat,tfrlon):tfrdata[0]}
                if len(tfr_bank)==0:
                    log.add({"Time to first packet(ms)":time.ticks_ms()})
                    tfr_bank.update(tfr)
        if time.ticks_ms() >= switchtime:
            display.show("1")
            ch = 1
            radio.config(group = ch)
            switchtime = time.ticks_add(time.ticks_ms(),itvl_ch1)

    for i, j in tfr_bank:
        d = nmeaparser.hav_formula(cl_dd,nmeaparser.dec_deg(i[0],i[1]))
        if d < j+1:
            log.add({"Time triggered(ms)":time.ticks_ms()})
            log.add({"Distance traveled when triggered(m)":nmeaparser.hav_formula(cl_dd,nmeaparser.dec_deg(init_loc["lat"],init_loc["lon"]))})
            log.add({"Distance from TFR when triggered(m)":d})
            log.add({"Avoidance success":nmeaparser.hav_formula(cl_dd,nmeaparser.dec_deg(i["lat"],i["lon"])) > d})
            volt = 0
            auton = True
            display.clear()
            display.show(Image.SAD)
    cutebot.set_motors_speed(volt,volt)

