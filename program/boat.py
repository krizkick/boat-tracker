import math


class Boat:
    def __init__(self):
        self._latitude = 0
        self._longitude = 0
        self._speed = 0        # knop
        self._course = 0       # grader fra nord, med klokka
        self._msgtime = ""

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def speed(self):
        return self._speed

    @property
    def course(self):
        return self._course

    def oppdater_info(self, msgtime, lat=None, long=None, speed=None, retning=None):
        if self._msgtime == msgtime:
            return False
        self._msgtime = msgtime
        if self._nyinfo(lat):
            self._latitude = lat
        if self._nyinfo(long):
            self._longitude = long
        if self._nyinfo(speed) and speed < 102.3:      # AIS: 102.3 = ukjent fart
            self._speed = speed
        if self._nyinfo(retning) and retning < 360:    # AIS: 360 = ukjent kurs
            self._course = retning
        return True

    def _nyinfo(self, var):
        return var is not None

    def boat_future_position(self, minutter: int):
        distanse = self._speed * minutter / 3600       # grader (1 nm = 1/60 grad)
        ny_breddegrad = self._latitude + distanse * math.cos(math.radians(self._course))
        ny_lengdegrad = self._longitude + distanse * math.sin(math.radians(self._course)) / math.cos(math.radians(self._latitude))
        return {
            "future_latitude": ny_breddegrad,
            "future_longitude": ny_lengdegrad,
            "latitude": self._latitude,
            "longitude": self._longitude,
            "minutter": minutter,
        }