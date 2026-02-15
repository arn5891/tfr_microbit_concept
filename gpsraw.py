from microbit import *
import log

#with the motor kit attached to the microbit, pins 19 and 20 are the easiest to dedicate to UART
uart.init(baudrate=9600, bits=8, parity=None, stop=1, tx=pin19, rx=pin20)

#Set update rate to 1000 milliseconds (1Hz)
uart.write(b"$PMTK220,1000*1F\x0D\x0A")

#send the configuration bytes that the example provides:
# Ask for specific data to be sent.
#                    A B C D E F G H                   I
uart.write(b'$PMTK314,1,1,5,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0*29\r\n')

#   A - send GLL sentences
#   B - send RMC sentences
#   C - send VTG sentences
#   D - send GGA sentences
#   E - send GSA sentences
#   F - send GSV sentences
#   G - send GRS sentences
#   H - send GST sentences
#   I - send ZDA sentences

# The number is how often to send the sentence compared to the update frequency.
# If the update frequency is 500ms and the number is 5, it will send that message
# every 2.5 seconds.


#create a variable to store received sentences in
msg = ""

while(True):
    if uart.any():
        # A valid sentence was received - log it to microbit's data log
        msg = str(uart.read())
        log.add({"test":msg})
        display.show(msg)
    else:
        # No valid sentence was received, wait a moment, display image for debugging purposes.
        display.show(Image.SAD)
        sleep(100)
    display.clear()
    sleep(100)
