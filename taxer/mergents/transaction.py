class Transaction:
    __unit = None
    __time = None
    __amount = None

    def __init__(self, unit, time, amount):
        self.__unit = unit
        self.__time = time
        self.__amount = amount
