import serial
from serial import Serial
import time


class mode:
    LOW = 0
    HIGH = 1
    DIGITAL = 2
    ANALOG = 3

    UltraSonicGet = 255


class Arduino:
    def digitalWrite(self, pin, val):
        self.port.write(bytes([mode.DIGITAL, pin, val]))

    def analogWrite(self, pin, val):
        self.port.write(bytes([mode.ANALOG, pin, val]))

    def sonicRead(self, trig, echo):
        self.port.write(bytes([mode.UltraSonicGet, trig, echo]))
        return list(self.port.read(1))[0]

    def close(self):
        self.port.close()

    def __init__(self, portName: str):
        self.port = Serial(portName, baudrate=9600,
                           stopbits=serial.STOPBITS_ONE,
                           parity=serial.PARITY_NONE,
                           bytesize=serial.EIGHTBITS)

        time.sleep(2)

    def __del__(self):
        self.close()
