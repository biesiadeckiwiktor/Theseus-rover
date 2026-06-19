from machine import Pin, PWM, UART
import network
import socket
import struct
import time


USE_WIFI = False  # True = WiFi, False = HC-12

AP_SSID = "theseus"
AP_PASSWORD = "12345678"
PORT = 5005

uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1)) 

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
    hc12 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

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

    time.sleep(0.02)