class Currency:
    __satoshiToBTC = 0.00000001

    def __init__(self, unit, amount):
        self.__unit = unit
        self.__amountRaw = 0.0 if amount == '' else float(amount)
        self.__amount = abs(self.__amountRaw)
        if self.__unit == 'satoshi':
            self.__unit = 'BTC'
            self.__amountRaw = self.__amountRaw * Currency.__satoshiToBTC
            self.__amount = self.__amount * Currency.__satoshiToBTC

    @property
    def unit(self):
        return self.__unit

    @property
    def amount(self):
        return self.__amount

    @property
    def amountRaw(self):
        return self.__amountRaw

    def __add__(self, other):
        if self.unit != other.unit:
            raise "Currency not the same; self={}, other={}".format(self.unit, other.unit)
        return Currency(self.unit, self.amount + other.amount)

    def __sub__(self, other):
        if self.unit != other.unit:
            raise "Currency not the same; self={}, other={}".format(self.unit, other.unit)
        return Currency(self.unit, self.amount - other.amount)

    def __str__(self):
        return "{} {}".format(self.__amount, self.__unit)
