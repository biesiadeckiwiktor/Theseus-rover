'''
encoders.py - quadrature encoder reader using PIO
Adapted from:
SPDX-FileCopyrightText: 2022 Jamon Terrell <github@jamonterrell.com>
SPDX-License-Identifier: MIT
https://github.com/jamon/pi-pico-pio-quadrature-encoder/blob/main/python/quadrature.py

Changes include fifo cleanup and initialising pull up on encoder pins to high by default 
'''
from rp2 import PIO, StateMachine, asm_pio
from machine import Pin


@asm_pio(autopush=True, push_thresh=32)
def _encoder_pio():
    wait(0, pin, 0)
    jmp(pin, "WAIT_HIGH")
    mov(x, invert(x))
    jmp(x_dec, "nop1")
    label("nop1")
    mov(x, invert(x))
    label("WAIT_HIGH")
    jmp(x_dec, "nop2")
    label("nop2")
    wait(1, pin, 0)
    jmp(pin, "WAIT_LOW")
    jmp(x_dec, "nop3")
    label("nop3")
    label("WAIT_LOW")
    mov(x, invert(x))
    jmp(x_dec, "nop4")
    label("nop4")
    mov(x, invert(x))
    wrap()


class Encoder:
    def __init__(self, sm_id, clk_pin, data_pin):
        Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        Pin(data_pin, Pin.IN, Pin.PULL_UP)
        self._sm = StateMachine(
            sm_id, _encoder_pio, freq=125_000_000,
            in_base=Pin(clk_pin), jmp_pin=Pin(data_pin)
        )
        self._sm.active(1)

    def read(self):
        while self._sm.rx_fifo():          
            self._sm.get()
        self._sm.exec("in_(x, 32)")
        x = self._sm.get()
        return x if x < 0x80000000 else x - 0x100000000

    def stop(self):
        self._sm.active(0)