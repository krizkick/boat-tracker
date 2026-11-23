from machine import RTC, deepsleep, Pin, SPI 
import urequests as requests
import secrets
import network
import time
from epd42 import EPD
from neopixel import NeoPixel


def get_new_version():
    rtc = RTC()
    stored = rtc.memory()
    previous = int(stored) if stored else -1
    request = requests.get(url=secrets.VERSION_LINK)
    try:
        new = int(request.text)
    finally:
        request.close()
    print("forrige:", previous, "ny:", new)
    return new if new != previous else None

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        for _ in range(20):
            if wlan.isconnected():
                break
            time.sleep(1)
    print(wlan.ifconfig())
    return wlan

def update_image():
    spi = SPI(1, baudrate=4_000_000, polarity=0, phase=0,
               sck=Pin(11), mosi=Pin(12))
    epd = EPD(spi, cs=5, dc=17, rst=16, busy=4)
    request = requests.get(url=secrets.MAP_LINK)
    try:
        map_data = request.content
    finally:
        request.close()

    epd.init()
    epd.show(map_data)
    print("busy:", epd.busy.value())  # hvis busy er et Pin-attributt
    time.sleep(10)
    epd.sleep()


print("starter nettverk")
connect_wifi()
print("nettverk ferdi")

new = get_new_version()
if new is not None:
    print("oppdaterer bilde")
    update_image()
    RTC().memory(str(new).encode())
deepsleep(300000)