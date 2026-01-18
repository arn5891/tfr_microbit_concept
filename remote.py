from microbit import *
import radio

display.set_pixel(0,0,9)
radio.on()
radio.config(group=1)
radio.config(power=1)
radio.config(group=1)
while True:
    snd = ""
    if button_a.is_pressed():
        snd+="A"
    if button_b.is_pressed():
        snd+="B"
    radio.send(snd)
