import collections
from datetime import datetime
from datetime import timedelta
import time
from pytz import utc


class Throttler:
    __unit = timedelta(seconds=1)

    def __init__(self, callsPerSecond: int):
        self.__calls = collections.deque(maxlen=callsPerSecond)

    def throttle(self):
        self.__calls.append(datetime.now(utc))
        size = len(self.__calls)
        if size < self.__calls.maxlen:
            return
        newest = self.__calls[0]
        oldest = self.__calls[size-1]
        difference = newest - oldest
        if difference > Throttler.__unit:
            return
        wait = (Throttler.__unit - difference).microseconds / 1000000
        time.sleep(wait)