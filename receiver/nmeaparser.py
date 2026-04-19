import math
from microbit import *
BAD_MSG = ["?"]
DIG="1234567890"
uart.init(baudrate=9600, tx = pin1, rx = pin2)

def parse(_id, delim = ","):
    done = False
    sent = ""
    while !done:
        if uart.any():
            rd = uart.read()
            if sent == "" and "$"+_id in rd:
                sent = rd[rd.find("$"+_id+delim)+len("$"+_id+delim):]
            if sent != "" and "*" in sent:
                sent = rd[:rd.find("*")
                done = True
    ret = sent.split(delim)
    no = False
    if ret[1] == "" or ret[2] == "" or ret[3] == "" or ret[4] == "":
               no = True
    return BAD_MSG if no else sent

def dec_deg(lat,lon):
    nulat = (float(lat[0][:2])+(float(lat[0][2:])/60.0)) * (-1.0 if (lat[1] == "S") else 1.0)  
    nulon = (float(lon[0][:3])+(float(lon[0][3:])/60.0)) * (-1.0 if (lon[1] == "W") else 1.0)
    return [nulat, nulon]

#haversine formula
def hav_formula(p1,p2, km = False):
    lat1, lon1 = p1
    lat2, lon2 = p2
    R = 6371000
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2-lat1)
    delta_lambda = math.radians(lon2-lon1)
    a = math.sin(delta_phi/2.0)**2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda/2.0)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    m = R*c
    return m/1000 if km else m
