from machine import SPI, Pin
from epd42 import EPD

print("start")
spi = SPI(1, baudrate=4_000_000, polarity=0, phase=0,
          sck=Pin(11), mosi=Pin(12))
epd = EPD(spi, cs=5, dc=17, rst=16, busy=4)
print("BUSY før init:", epd.busy())

with open("kart.bin", "rb") as bilde:
    kart = bilde.read()
print("lest", len(kart))

epd.init()
print("init ferdig")
epd.show(kart)
print("show ferdig")
epd.sleep()
print("sove")