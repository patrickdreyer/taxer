from decimal import Decimal


class Shareholder:
    def __init__(self):
        self.__amount = Decimal()

    @property
    def amount(self):
        return self.__amount

    @property
    def percentage(self):
        return self.__percentage

    def add(self, amount):
        self.__amount = self.__amount + amount

    def correctPercentage(self, total):
        self.__percentage = self.__amount / total if total > Decimal() else Decimal(100)
