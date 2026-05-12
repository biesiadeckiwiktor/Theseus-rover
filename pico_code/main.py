from machine import Pin, PWM, UART
import network
import socket
import struct
import time


AP_SSID = "theseus"
AP_PASSWORD = "12345678"
PORT = 5005

uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

ap = network.WLAN(network.AP_IF)
ap.active(True)
while not ap.active():
    time.sleep(0.1)
ap.config(essid=AP_SSID, password=AP_PASSWORD)
print("AP active, IP:", ap.ifconfig()[0])


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', PORT))
sock.setblocking(False)  


START = 0xAA
END   = 0x55


while True:
    try:
        data, addr = sock.recvfrom(1024)
        if len(data) != 11:
            continue

        # unpack packet
        s = struct.unpack("BBBBBBBBBBB", data)
        if s[0] != START or s[10] != END:
            continue
        
        uart0.write(data)

        # joystick values 0-255
        j1a1, j1a2, j1a3 = s[1], s[2], s[3]
        j2a1, j2a2, j2a3 = s[4], s[5], s[6]

        # buttons
        btn_low, btn_mid, btn_high = s[7], s[8], s[9]
        buttons = (btn_high << 16) | (btn_mid << 8) | btn_low

        # triggers
        left_trigger  = bool(buttons & (1 << 16))
        right_trigger = bool(buttons & (1 << 17))

        # print for debug
        print("J1:", j1a1, j1a2, j1a3, 
              "J2:", j2a1, j2a2, j2a3,
              "Buttons: {:016b}".format(buttons),
              "L_TRG:", left_trigger, "R_TRG:", right_trigger)


    except OSError:
        pass

    time.sleep(0.02)
