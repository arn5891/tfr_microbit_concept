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
            tfr = [tfr_dd,float(radius)]
    if tfr is not nmeaparser.BAD_MSG and not tfr in tfr_bank:
        log.add({"Time to first packet(ms)":time.ticks_ms()-starttime})
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
ERROR_MARGIN = 0
MAX_SPEED = 80
BUFFER = 1
auton = False
end = False
start = False
starttime = 0
volt = 0
accel = 0
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
radio.config(group = ch)
radio.config(power = 1)
radio.config(length = 100)

while start is not True:
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
    rad_msg = radio.receive()
    if rad_msg is not None:
        start = True
        
starttime = time.ticks_ms()
switchtime = time.ticks_add(starttime, itvl_ch1)
display.clear()

while end is False:
    display.show(ch)
    #switch channel
    if time.ticks_ms() >= switchtime and auton is False:
        ch = 2 if ch==1 else 1
        switchtime = time.ticks_add(time.ticks_ms(),[itvl_ch1,itvl_ch2][ch-1])
        radio.config(group = ch)
        
    #attempt to get current location, get radio msgs
    cur_loc = update_loc(None)
    rad_msg = radio.receive()

    if ch == 1:
        if rad_msg == "1":
            accel = 0
            volt = 80
        else:
            accel = -1
    if ch == 2:
        if cur_loc is not None:
            cl_dd = nmeaparser.dec_deg(cur_loc["lat"],cur_loc["lon"])
            update_tfr(rad_msg)
            for i in tfr_bank:
                d = nmeaparser.hav_formula(i[0],cl_dd)-(ERROR_MARGIN*2)
                #log.add({"dist to tfr(+/- ERROR_MARGIN m) https://forum.arduino.cc/t/accuracy-of-neo6mv2/205205/2":d})
                if d <= i[1]+BUFFER:
                    display.show(Image.DIAMOND)
                    #data recording
                    if auton is False:
                        log.add({"intervals(ms, 1-2)":str(itvl_ch1)+","+str(itvl_ch2)})
                        log.add({"Time auton triggered(ms)":time.ticks_ms()-starttime})
                        log.add({"Distance traveled when auton triggered(m)":nmeaparser.hav_formula(cl_dd,il_dd)})
                        log.add({"Distance from TFR when auton triggered(m)":d})
                    auton = True
                    MAX_SPEED = 80*((d-i[1])/BUFFER)
    
    volt = volt + accel
    volt = min(volt, MAX_SPEED)
    if volt <= 2:
        volt = 0
        end = True
    cutebot.set_motors_speed(round(volt),round(volt))
