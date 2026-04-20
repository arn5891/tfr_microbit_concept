import math
from microbit import *
BAD_MSG = ["?"]
DIG="1234567890"
uart.init(baudrate=9600, tx = pin1, rx = pin2)

def parse(_id, otherinput=None, delim=","):
    sent = ""
    prefix = "$" + _id + delim

    while True:
        if otherinput is not None:
            rd = otherinput
            rd = str(rd)
        else:
            if not uart.any():
                continue
            rd = uart.read()
            if not rd:
                continue
            rd = str(rd)

        sent += rd

        start = sent.find(prefix)
        if start == -1:
            if len(sent) > 2000:
                sent = sent[-2000:]
            continue

        sent = sent[start + len(prefix):]

        end = sent.find("*")
        if end == -1:
            if len(sent) > 2000:
                sent = sent[-2000:]
            continue

        sent = sent[:end]

        ret = sent.split(delim)
        return ret

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
