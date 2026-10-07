import sys
import struct
import time

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    sys.exit("pyserial missing. Run: sudo apt install python3-serial")

try:
    import pygame
except ImportError:
    sys.exit("pygame missing. Run: sudo apt install python3-pygame")

START = 0xAA
END   = 0x55
BAUD  = 9600

BIT_ZERO_TURN = 17 

def find_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if p.vid == 0x10C4 or "CP210" in (p.description or ""):
            print(f"Found CP2102 on {p.device}")
            return p.device
    for p in ports:
        if "ttyUSB" in p.device or "COM" in p.device:
            print(f"CP2102 not identified, using {p.device}")
            return p.device
    sys.exit("No serial port found. Is the CP2102 plugged in?")

ser = serial.Serial(find_port(), BAUD)

def send_packet(j1a0, j1a2, j2a1, buttons):
    btn_low  = buttons & 0xFF
    btn_mid  = (buttons >> 8) & 0xFF
    btn_high = (buttons >> 16) & 0xFF
    packet = struct.pack("BBBBBBBBBBB",
        START,
        j1a0, 128, j1a2,   
        128, j2a1, 128,   
        btn_low, btn_mid, btn_high,
        END)
    ser.write(packet)

pygame.init()
screen = pygame.display.set_mode((360, 120))
pygame.display.set_caption("Rover control - WASD, O = zero turn")
font = pygame.font.SysFont(None, 28)

zero_turn_mode = False 

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
            zero_turn_mode = not zero_turn_mode

    keys = pygame.key.get_pressed()

    j1a0 = 128
    j1a2 = 128
    j2a1 = 128
    buttons = 0

    if keys[pygame.K_w]: j1a0 = 0
    if keys[pygame.K_s]: j1a0 = 255
    if keys[pygame.K_a]:
        j2a1 = 255
        j1a2 = 255
    if keys[pygame.K_d]:
        j2a1 = 0
        j1a2 = 0

    if keys[pygame.K_o]:
        buttons |= (1 << BIT_ZERO_TURN)

    send_packet(j1a0, j1a2, j2a1, buttons)

    screen.fill((30, 30, 30))
    mode = "ZERO TURN" if zero_turn_mode else "NORMAL"
    screen.blit(font.render(f"Mode: {mode}", True, (255, 200, 0)), (20, 25))
    screen.blit(font.render(f"Drive: {j1a0}  Steer: {j2a1}", True, (255, 255, 255)), (20, 65))
    pygame.display.flip()

    time.sleep(0.1)

ser.close()
pygame.quit()