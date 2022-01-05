from decimal import Decimal

from .shareholder import Shareholder


class Shareholders:
    def __init__(self):
        self.__dict = dict()

    def add(self, opening):
        name = opening['Name']
        if not name in self.__dict:
            self.__dict[name] = Shareholder()
        shareholder = self.__dict[name]
        shareholder.add(Decimal(opening['Amount']))
        total = sum([s.amount for s in self.__dict.values()], Decimal())
        for shareholder in self.__dict.values():
            shareholder.correctPercentage(total)
