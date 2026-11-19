from machine import Pin, SPI
from time import sleep_ms

W, H = 400, 300

class EPD:
    def __init__(self, spi, cs, dc, rst, busy):
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT, value=1)
        self.dc = Pin(dc, Pin.OUT, value=0)
        self.rst = Pin(rst, Pin.OUT, value=1)
        self.busy = Pin(busy, Pin.IN)

    def _cmd(self, c, data=None):
        self.cs(0)
        self.dc(0)
        self.spi.write(bytes([c]))
        if data is not None:
            self.dc(1)
            self.spi.write(data)
        self.cs(1)

    def _wait(self):
        while self.busy():          # HIGH = opptatt
            sleep_ms(10)

    def init(self):
        self.rst(0); sleep_ms(10)
        self.rst(1); sleep_ms(10)
        self._wait()
        self._cmd(0x12)             # software reset
        self._wait()
        self._cmd(0x01, bytes([(H - 1) & 0xFF, (H - 1) >> 8, 0x00]))
        self._cmd(0x21, b"\x40\x00")
        self._cmd(0x3C, b"\x05")    # border
        self._cmd(0x11, b"\x03")    # x+, y+
        self._cmd(0x44, bytes([0x00, W // 8 - 1]))
        self._cmd(0x45, bytes([0, 0, (H - 1) & 0xFF, (H - 1) >> 8]))
        self._cmd(0x4E, b"\x00")
        self._cmd(0x4F, b"\x00\x00")
        self._wait()

    def show(self, buf):
        """buf: 15000 byte, 1 bit/piksel, 1 = hvit, 0 = svart."""
        self._cmd(0x4E, b"\x00")
        self._cmd(0x4F, b"\x00\x00")
        self._cmd(0x24, buf)
        self._cmd(0x4E, b"\x00")
        self._cmd(0x4F, b"\x00\x00")
        self._cmd(0x26, buf)        # samme data i begge RAM = ren full refresh
        self._cmd(0x22, b"\xF7")
        self._cmd(0x20)
        self._wait()

    def sleep(self):
        self._cmd(0x10, b"\x01")