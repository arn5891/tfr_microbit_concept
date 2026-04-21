from microbit import *
import nmeaparser
import cutebot
import log
import radio
import time
import math
import music

def bprint(s):
    uart.init(115200)
    print(str(s)+"\n")
    uart.init(baudrate=9600, tx = pin1, rx = pin2)



def update_loc(v):
    sntc = nmeaparser.parse("GPGGA")
    bad = sntc[1] == "" or sntc[2] == "" or sntc[3] == "" or sntc[4] == ""
    if not bad:
        if sntc[5] != "0":
            return {"lat":[sntc[1], sntc[2]], "lon":[sntc[3], sntc[4]]}
    return v

def update_tfr(m):
    tfr = nmeaparser.BAD_MSG
    #bprint("start of update_tfr. m is "+str(m))
    if m is not None:
        tfrdata = nmeaparser.parse("TFR", otherinput = m)
        #bprint("finished parsing")
        if tfrdata != nmeaparser.BAD_MSG:
            tfrlat = [tfrdata[1],tfrdata[2]]
            tfrlon = [tfrdata[3],tfrdata[4]]
            tfr_dd = nmeaparser.dec_deg(tfrlat,tfrlon)
            radius = tfrdata[0]
            tfr = [tfr_dd,float(radius)]
    if tfr != nmeaparser.BAD_MSG and not tfr in tfr_bank:
        display.show("T")
        log.add({"Time to first packet(ms)":time.ticks_ms()-starttime})
        tfr_bank.append(tfr)
        #bprint("yay")

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
error_sum = 0
MAX_SPEED = 40
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
maintfr = None
uart_msg = ""
init_loc = None
while init_loc is None:
    init_loc = update_loc(init_loc)
il_dd = nmeaparser.dec_deg(init_loc["lat"],init_loc["lon"])
cur_loc = {"lat":init_loc["lat"],"lon":init_loc["lon"]}
cl_dd = nmeaparser.dec_deg(cur_loc["lat"],cur_loc["lon"])

'''
#error margin calculations
rng = 20
for i in range(rng):
    error = None
    while error is None:
        error = update_loc(None)
    e_dd = nmeaparser.dec_deg(error["lat"],error["lon"])
    e_dist = nmeaparser.hav_formula(il_dd, e_dd)
    error_sum = e_dist**2 + error_sum
    display.clear()
    for j in range(round((i+1)/rng*5)):
        display.set_pixel(j,0,9)
ERROR_MARGIN = math.sqrt((1/(rng-1))*error_sum)
#bprint("error margin"+str(ERROR_MARGIN))
display.clear()
'''
#display listening intervals- A side for ch1(remote), B side for ch2(TX)
display.set_pixel(0,itvl_ch1//30-1,9)
display.set_pixel(4,itvl_ch2//30-1,9)

#config
radio.on()
radio.config(channel = ch)
radio.config(power = 1)
radio.config(length = 100)
radio.config(data_rate = radio.RATE_2MBIT)

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
        
display.clear()
starttime = time.ticks_ms()
switchtime = time.ticks_add(starttime, itvl_ch1)

while end is False:
    #switch channel
    if auton is False and time.ticks_ms() >= switchtime:
        ch = 40 if ch==1 else 1
        switchtime = time.ticks_add(time.ticks_ms(),[itvl_ch1,itvl_ch2][ch==1])
        radio.config(channel = ch)
        #display.show(int(ch==40))
        #bprint("switch to "+str(ch))
        
    rad_msg = radio.receive()
    bprint(rad_msg)
    #attempt to get current location, get radio msgs
    cur_loc = update_loc(cur_loc)
    #bprint(str(cur_loc))
    if ch == 1:
        rad_msg = radio.receive()
        if rad_msg == '1':
            volt = 40
        if rad_msg == '0':
            volt = 0
    if ch == 40:
        rad_msg = radio.receive()
        if cur_loc is not None:
            cl_dd = nmeaparser.dec_deg(cur_loc["lat"],cur_loc["lon"])
            #bprint('checking for tfr')
            update_tfr(rad_msg)
            #bprint('done w check. end is '+str(end))
            for i in tfr_bank:
                d = nmeaparser.hav_formula(i[0],cl_dd)
                #bprint(d)
                if d <= (i[1]+BUFFER+ERROR_MARGIN):
                    #bprint(str(d)+" vs " +str(i[1]+BUFFER+ERROR_MARGIN))
                    display.show(Image.DIAMOND)
                    #data recording
                    if auton is False:
                        log.add({"intervals(ms, 1-2)":str(itvl_ch1)+","+str(itvl_ch2)})
                        log.add({"Time auton triggered(ms)":time.ticks_ms()-starttime})
                        log.add({"Distance traveled when auton triggered(m)":nmeaparser.hav_formula(cl_dd,il_dd)})
                        log.add({"Distance from TFR when auton triggered(m)":d})
                    auton = True
                    volt = 0
                    end = True
                    #maintfr = i
                    break
            '''if auton is True and maintfr is not None:
                dtoborder = nmeaparser.hav_formula(maintfr[0],cl_dd)-(ERROR_MARGIN*2)-maintfr[1]
                a = accelerometer.get_z() * 0.00980665
                volt = round(math.sqrt((volt*volt)+(2*a*dtoborder)))
                if volt < 5:
                    volt = 0
                    end = True'''
    #bprint(str(ch)+str(auton)+str(volt))
    cutebot.set_motors_speed(volt,volt)
