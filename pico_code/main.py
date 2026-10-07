from machine import Pin, PWM, UART
import network
import socket
import struct
import time
from encoders import Encoder
import utime

# encoder pins
enc0 = Encoder(0, 17, 16)   #fr
enc1 = Encoder(1, 19, 18)   #mr
enc2 = Encoder(2, 14, 15)   #rr
enc3 = Encoder(3, 13, 12)   #ml
enc4 = Encoder(4, 11, 10)   #fl
enc5 = Encoder(5, 9, 8)     #rl

#hc-12 module pins
hc_12_tx = 4
hc_12_rx = 5

#UART pins for pico - arduino communication
uart0_tx = 0
uart0_rx = 1

#remote control
USE_WIFI = False  # True = WiFi, False = HC-12

AP_SSID = "theseus"
AP_PASSWORD = "12345678"
PORT = 5005

uart0 = UART(0, baudrate=9600, tx=Pin(uart0_tx), rx=Pin(uart0_rx)) 

if USE_WIFI:
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    while not ap.active():
        time.sleep(0.1)
    ap.config(essid=AP_SSID, password=AP_PASSWORD)
    print("AP active, IP:", ap.ifconfig()[0])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', PORT))
    sock.setblocking(False)
else:
    hc12 = UART(1, baudrate=9600, tx=Pin(hc_12_tx), rx=Pin(hc_12_rx))

START = 0xAA
END   = 0x55

while True:
    if USE_WIFI:
        try:
            data, addr = sock.recvfrom(1024)
            if len(data) != 11:
                continue
            s = struct.unpack("BBBBBBBBBBB", data)
            if s[0] != START or s[10] != END:
                continue
            uart0.write(data)
        except OSError:
            pass
    else:
        if hc12.any():
            data = hc12.read(11)
            if data and len(data) == 11:
                s = struct.unpack("BBBBBBBBBBB", data)
                if s[0] == START and s[10] == END:
                    uart0.write(data)
                    
    print(enc0.read(),enc1.read(),enc2.read(),enc3.read(),enc4.read(),enc5.read())

    time.sleep(0.02)