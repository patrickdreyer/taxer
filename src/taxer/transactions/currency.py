from decimal import Decimal


class Currency:
    __satoshiToBTC = Decimal(0.00000001)

    def __init__(self, unit, amount):
        self.__unit = unit
        self.__amountRaw = Decimal() if amount == '' else Decimal(amount)
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
        if other.amount == 0:
            return self
        if self.unit != other.unit:
            raise Exception(f'Currency not the same; self={self.unit}, other={other.unit}')
        return Currency(self.unit, self.amount + other.amount)

    def __sub__(self, other):
        if other.amount == 0:
            return self
        if self.unit != other.unit:
            raise Exception(f'Currency not the same; self={self.unit}, other={other.unit}')
        return Currency(self.unit, self.amount - other.amount)

    def __str__(self):
        return "{} {}".format(self.__amount, self.__unit)
