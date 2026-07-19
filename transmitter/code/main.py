from machine import Pin, I2C, ADC
from DIYables_MicroPython_LCD_I2C import LCD_I2C
import time
import ads1x15
import utime
import network
import socket
import struct

SSID = "theseus"
PASSWORD = "12345678"

IP = "192.168.4.1"
PORT = 5005

START = 0xAA
END = 0x55

i2c0 = I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)
i2c1 = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)

I2C_ADDR = 0x27
LCD_ROWS = 2
LCD_COLS = 16

lcd = LCD_I2C(i2c0, I2C_ADDR, LCD_ROWS, LCD_COLS)

ads0 = ads1x15.ADS1115(i2c1, 0x48)
ads1 = ads1x15.ADS1115(i2c1, 0x49)

red = Pin(18, Pin.OUT)
yellow_1 = Pin(19, Pin.OUT)
yellow_2 = Pin(20, Pin.OUT)
green = Pin(21, Pin.OUT)

time.sleep(2)

lcd.print("Hello :)")

red(1)
yellow_1(1)
yellow_2(1)
green(1)

wifi = network.WLAN(network.STA_IF)
wifi.active(True)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

row_pins = [Pin(p, Pin.IN, Pin.PULL_DOWN) for p in (6,7,8,9)]
col_pins = [Pin(p, Pin.OUT) for p in (10,11,12,13)]

adc = ADC(Pin(28))

key_map = (
    (1,4,7,"*"),
    (2,5,8,"0"),
    (3,6,9,"#"),
    ("A","B","C","D")
)

key_to_bit = {
    1:0, 2:1, 3:2,
    4:3, 5:4, 6:5,
    7:6, 8:7, 9:8,
    "0":9, "*":10, "#":11,
    "A":12, "B":13, "C":14, "D":15
}

buttonL = Pin(14, Pin.IN, Pin.PULL_UP)
buttonR = Pin(15, Pin.IN, Pin.PULL_UP)

red(0)
yellow_1(0)
yellow_2(0)
green(0)

def scan_keypad():
    for c, col in enumerate(col_pins):
        col.on()
        for r, row in enumerate(row_pins):
            if row.value():
                col.off()
                return key_map[r][c]
        col.off()
    return None

def read_voltage(adc, ch):
    raw = adc.read(4, ch)
    return adc.raw_to_v(raw)

def connect_wifi():
    if wifi.isconnected():
        return True
    print("Connecting wifi...")
    lcd.clear()
    lcd.print("Connecting")
    lcd.set_cursor(0, 1)
    lcd.print("wifi...")
    lcd.set_cursor(0, 0)
    try:
        wifi.disconnect()
    except:
        pass
    time.sleep(2)
    wifi.connect(SSID, PASSWORD)
    timeout = 20
    while not wifi.isconnected() and timeout > 0:
        print("Waiting for connection...")
        lcd.clear()
        lcd.print("Waiting for")
        lcd.set_cursor(0, 1)
        lcd.print("connection...")
        lcd.set_cursor(0, 0)
        time.sleep(1)
        timeout -= 1
    if wifi.isconnected():
        print("Connected:", wifi.ifconfig())
        lcd.clear()
        lcd.print("Connected")
        return True
    else:
        print("Connection failed")
        lcd.clear()
        lcd.print("Connection")
        lcd.set_cursor(0, 1)
        lcd.print("failed")
        lcd.set_cursor(0, 0)
        return False

def voltage_to_byte(v):
    v = max(0, min(3.3, v))
    return int(v / 3.3 * 255)

while not connect_wifi():
    time.sleep(2)

def rssi_to_bars(rssi):
    if rssi >= -50: return 8
    elif rssi >= -55: return 7
    elif rssi >= -60: return 6
    elif rssi >= -65: return 5
    elif rssi >= -70: return 4
    elif rssi >= -75: return 3
    elif rssi >= -80: return 2
    else: return 1

def show_signal(rssi):
    lcd.clear()
    bars = rssi_to_bars(rssi)
    lcd.set_cursor(0, 0)
    lcd.print("{:4d}dB".format(rssi))
    for i in range(8):
        lcd.set_cursor(8 + i, 0)
        lcd.print(chr(signal_top[bars - 1][i]))
    for i in range(8):
        lcd.set_cursor(8 + i, 1)
        lcd.print(chr(signal_bot[bars - 1][i]))

signal = 0
last_key = None

p0 = [0b00000]*8
p20 = [0,0,0,0,0,0,0b11111,0b11111]
p40 = [0,0,0,0,0b11111,0b11111,0b11111,0b11111]
p60 = [0,0,0b11111,0b11111,0b11111,0b11111,0b11111,0b11111]
p80 = [0b11111]*8

lcd.custom_char(0, p0)
lcd.custom_char(1, p20)
lcd.custom_char(2, p40)
lcd.custom_char(3, p60)
lcd.custom_char(4, p80)

signal_bot = [
    [1,0,0,0,0,0,0,0],
    [1,2,0,0,0,0,0,0],
    [1,2,3,0,0,0,0,0],
    [1,2,3,4,0,0,0,0],
    [1,2,3,4,4,0,0,0],
    [1,2,3,4,4,4,0,0],
    [1,2,3,4,4,4,4,0],
    [1,2,3,4,4,4,4,4],
]

signal_top = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,1,0,0,0],
    [0,0,0,0,1,2,0,0],
    [0,0,0,0,1,2,3,0],
    [0,0,0,0,1,2,3,4],
]

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

while True:
    adc_value = adc.read_u16() >> 4
    voltage = map_value(adc_value, 0, 4095, 0, 3.3)

    if voltage > 2.8:
        red.on(); yellow_1.on(); yellow_2.on(); green.on()
    elif 2.8 >= voltage > 2.6:
        red.on(); yellow_1.on(); yellow_2.on(); green.off()
    elif 2.6 >= voltage > 2.4:
        red.on(); yellow_1.on(); yellow_2.off(); green.off()
    else:
        red.on(); yellow_1.off(); yellow_2.off(); green.off()

    if not wifi.isconnected():
        lcd.clear()
        lcd.print("Signal lost")
        while not connect_wifi():
            time.sleep(2)
        continue

    v0 = read_voltage(ads0, 0)
    v1 = read_voltage(ads0, 1)
    v2 = read_voltage(ads0, 2)
    v3 = read_voltage(ads1, 0)
    v4 = read_voltage(ads1, 1)
    v5 = read_voltage(ads1, 2)

    j1a0 = voltage_to_byte(v0)
    j1a1 = voltage_to_byte(v1)
    j1a2 = voltage_to_byte(v2)
    j2a0 = voltage_to_byte(v3)
    j2a1 = voltage_to_byte(v4)
    j2a2 = voltage_to_byte(v5)

    buttons = 0
    key = scan_keypad()
    if key and key != last_key:
        print("Pressed:", key)
    if key in key_to_bit:
        buttons |= (1 << key_to_bit[key])
    last_key = key

    if not buttonL.value():
        buttons |= (1 << 16)
    if not buttonR.value():
        buttons |= (1 << 17)

    btn_low  = buttons & 0xFF
    btn_mid  = (buttons >> 8) & 0xFF
    btn_high = (buttons >> 16) & 0xFF

    packet = struct.pack(
        "BBBBBBBBBBB",
        START, j1a0, j1a1, j1a2,
        j2a0, j2a1, j2a2,
        btn_low, btn_mid, btn_high,
        END
    )

    try:
        sock.sendto(packet, (IP, PORT))
    except:
        pass

    rssi = wifi.status('rssi')
    show_signal(rssi)

    time.sleep(0.1)