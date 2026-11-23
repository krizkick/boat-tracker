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

    def update_info(self, msg_time, lat=None, long=None, speed=None, direction=None):
        if self._msgtime == msg_time:
            return False
        self._msgtime = msg_time
        if self._has_new_info(lat):
            self._latitude = lat
        if self._has_new_info(long):
            self._longitude = long
        if self._has_new_info(speed) and speed < 102.3:      # AIS: 102.3 = ukjent fart
            self._speed = speed
        if self._has_new_info(direction) and direction < 360:    # AIS: 360 = ukjent kurs
            self._course = direction
        return True

    def _has_new_info(self, value):
        return value is not None

    def boat_future_position(self, minutes: int):
        distance = self._speed * minutes / 3600       # grader (1 nm = 1/60 grad)
        new_latitude = self._latitude + distance * math.cos(math.radians(self._course))
        new_longitude = self._longitude + distance * math.sin(math.radians(self._course)) / math.cos(math.radians(self._latitude))
        return {
            "future_latitude": new_latitude,
            "future_longitude": new_longitude,
            "latitude": self._latitude,
            "longitude": self._longitude,
            "minutes": minutes,
        }