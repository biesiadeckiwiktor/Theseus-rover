Theseus Rover

A low-cost, open-source 6-wheeled rover platform for education, research, and DIY robotics.

Theseus is inspired by planetary exploration rovers such as ESA's Rosalind Franklin (ExoMars) and CSA's MESR and REX. It can be built entirely from 3D-printed parts and components that are widely available worldwide — no machining or custom PCBs required.


Total cost: under $800 / £600, including the cost of a 3D printer
Two steering configurations: assemble as 4-wheel-steer (4WS) or 6-wheel-steer (6WS) using the same set of printed parts
Modular chassis built from 2020 aluminium extrusion, so it's easy to extend with sensors, cameras, or a robotic arm


<div align="center">
<img width="240" height="240" alt="Theseus rover performing a zero-radius turn" src="https://github.com/user-attachments/assets/3c71be6e-8ea9-4a64-800e-988696c8608a" />
<br><br>
<img width="483" height="330" alt="Theseus rover, front three-quarter view" src="https://github.com/user-attachments/assets/82ff3e5f-f62b-40a2-8775-d7363cfc0ce5" />
<img width="483" height="330" alt="Theseus rover, side view showing suspension" src="https://github.com/user-attachments/assets/06fb2d2c-030d-4de1-abe1-fd27ae40f261" />
</div>
Features


6-wheel drive — six JGA25-370 geared DC motors with encoders (one per wheel)
4WS / 6WS steering — four MG996R metal-gear servos steer the corner wheels; differential (Ackermann-style) steering geometry is computed on-board so all wheels track the correct turning radius
Zero-radius turning — spin on the spot at the press of a button
Custom handheld transmitter — dual joysticks, keypad, LCD with live signal strength, and a 3D-printed enclosure (~£76 in parts, design files included); supports the same Wi-Fi / HC-12 dual-mode link as the rover
Two radio link options — control over Wi-Fi (UDP, Pico acts as an access point) or long-range 433 MHz using an HC-12 module; switch with a single flag in the firmware
12V LiFePO4 power with DC-DC converters for logic and servo rails
Printable wheels — uses Lego 32298 tyres, with a fully 3D-printed alternative included (coming soon)


How it works

Theseus transmitter (custom handheld, Pico 2 W)
  dual joysticks · 4x4 keypad · 16x2 LCD · signal & battery indicators
        │
        │  Wi-Fi (UDP) or HC-12 433 MHz radio
        ▼
Raspberry Pi Pico 2 W (on rover)  ──  receives control packets, forwards over UART
        │
        ▼
Arduino Uno R3  ──  decodes packets, computes steering geometry (diffSteer library)
        │
        ├── 2× Adafruit Motor Shields  → 6× DC drive motors
        └── Adafruit 16-ch PWM Shield  → 4× steering servos

The diffSteer library (in arduino_code/) takes the rover's wheelbase and track widths and calculates the individual wheel speeds and steering angles needed for smooth, skid-free turns.

Control packet format

The transmitter sends an 11-byte packet at ~10 Hz. Anyone can write their own controller (phone app, PC gamepad script, etc.) by sending this frame over UDP to the rover's access point (192.168.4.1:5005) or over an HC-12 serial link:

ByteContent0Start marker 0xAA1–3Joystick 1 axes (0–255)4–6Joystick 2 axes (0–255)7–9Button states (24-bit bitmask: 16 keypad keys + 2 joystick buttons)10End marker 0x55

Repository contents

PathDescriptionCAD files/All 3D-printable and laser-cut parts in STEP formatarduino_code/Arduino Uno firmware: packet decoding, motor/servo control, and the diffSteer steering-geometry librarypico_code/Raspberry Pi Pico 2 W firmware (MicroPython): Wi-Fi/HC-12 receiver bridgetransmitter/Custom handheld transmitter: MicroPython firmware, 3D-printable enclosure (STEP), and its own bill of materialsBill of materials.xlsxFull costed parts list with supplier links

The transmitter

Theseus is driven with a purpose-built handheld transmitter (~£76 in parts) rather than an off-the-shelf gamepad:


Dual 4-axis joysticks sampled by two ADS1115 16-bit ADCs over I2C
4×4 matrix keypad for mode switching and auxiliary functions (e.g. zero-turn toggle)
16×2 LCD showing connection status and a live signal-strength bar graph (RSSI)
Battery level LEDs (4-stage indicator)
3D-printed enclosure — CAD in transmitter/cad/
Automatic reconnection if the radio link drops


See transmitter/bill of materials transmitter.ods for the full parts list.

Getting started

1. Print and source the parts

Open Bill of materials.xlsx for the complete parts list with prices and links. All structural parts in CAD files/ are provided as STEP files — slice and print them in PLA.

All parts were printed with 2 wall loops and 15% infill.

Structural integrity was tested with static weight of 60kg placed on top of the rover and no issues were observed, although for general use and depending on terrain up 15kg is recommended due to limited power of the motors. 

2. Assemble

The chassis is built around 2020 aluminium extrusion with printed brackets, joints, and covers. Choose 4WS or 6WS during assembly — both use the same printed parts.

Properly assembled wheels will hold pressure and act as pneumatic tyres.

Assembly instructions coming soon.

3. Flash the firmware

Raspberry Pi Pico 2 W (radio receiver):


Install MicroPython on the Pico
Copy pico_code/main.py to the board
Set USE_WIFI = True for Wi-Fi control or False for HC-12


Arduino Uno (motion controller):


Open arduino_code/arduino_code.ino in the Arduino IDE
Install the required libraries: Adafruit Motor Shield V2, Adafruit PWM Servo Driver
Upload to the board


4. Build and flash the transmitter


Source the parts in transmitter/bill of materials transmitter.ods (~£76) and print the enclosure from transmitter/cad/
Install MicroPython on the transmitter's Pico 2 W
Install the two required libraries by copying them to the board alongside the code:

ads1x15 — driver for the ADS1115 ADCs that read the joysticks
DIYables_MicroPython_LCD_I2C — driver for the 16×2 I2C LCD (also available via Thonny's package manager)



Copy transmitter/code/main.py to the board
Set USE_WIFI at the top of the file to match the rover (True = Wi-Fi, False = HC-12). For Wi-Fi mode, also fill in the rover's IP address



Note: if you use Wi-Fi mode, change the default access point password (AP_PASSWORD in pico_code/main.py and PASSWORD in the transmitter code) — anyone in range who knows the default could connect and send drive commands.



5. Drive

Power on the rover, then the transmitter — it connects to the rover's Wi-Fi access point automatically and reconnects if the link drops. One joystick controls speed, the other steering; the keypad handles auxiliary functions such as zero-turn mode.


Contributing

Contributions, bug reports, and build logs are very welcome! If you build a Theseus, please open an issue or discussion with photos — it helps others and improves the docs.

License

Code is released under the MIT License. Hardware design files are released under CERN-OHL-P / CC BY-SA 4.0.

Acknowledgements

Design inspired by ESA's Rosalind Franklin (ExoMars) rover and the Canadian Space Agency's MESR and REX rover prototypes.
