from machine import RTC, deepsleep, Pin, SPI 
import urequests as requests
import secrets
import network
import time
from epd42 import EPD
from neopixel import NeoPixel


def ny_versjon():
    rtc = RTC()
    lagret = rtc.memory()
    forrige = int(lagret) if lagret else -1
    request = requests.get(url=secrets.VERSJONLINK)
    try:
        ny = int(request.text)
    finally:
        request.close()
    print("forrige:", forrige, "ny:", ny)
    return ny if ny != forrige else None

def koble_til_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSORD)
        for _ in range(20):
            if wlan.isconnected():
                break
            time.sleep(1)
    print(wlan.ifconfig())
    return wlan

def oppdater_bilde():
    spi = SPI(1, baudrate=4_000_000, polarity=0, phase=0,
               sck=Pin(11), mosi=Pin(12))
    epd = EPD(spi, cs=5, dc=17, rst=16, busy=4)
    request = requests.get(url=secrets.KARTLINK)
    try:
        kart = request.content
    finally:
        request.close()

    epd.init()
    epd.show(kart)
    print("busy:", epd.busy.value())  # hvis busy er et Pin-attributt
    time.sleep(10)
    epd.sleep()

np = NeoPixel(Pin(48), 1)
np[0] = (0, 5, 0)
np.write()


print("starter nettverk")
koble_til_wifi()
print("nettverk ferdi")

ny = ny_versjon()
if ny is not None:
    print("oppdaterer bilde")
    oppdater_bilde()
    RTC().memory(str(ny).encode())
print("sove")
deepsleep(300000)