import collections
import datetime
import time


class Throttler:
    __unit = datetime.timedelta(seconds=1)

    def __init__(self, callsPerSecond):
        self.__calls = collections.deque(maxlen=callsPerSecond)

    def throttle(self):
        self.__calls.append(datetime.datetime.now())
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