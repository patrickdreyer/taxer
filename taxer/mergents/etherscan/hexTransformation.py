from decimal import Decimal


class HEXTransformation:
    def __init__(self, hex, eth):
        self.__hex = HEXTransformation.__clean(hex)
        self.__eth = HEXTransformation.__clean(eth)

    @property
    def hex(self):
        return self.__hex

    @property
    def eth(self):
        return self.__eth

    @staticmethod
    def __clean(values):
        value = ''.join(values)
        return Decimal(str.replace(value, ',', ''))
