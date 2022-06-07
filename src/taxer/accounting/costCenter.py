class CostCenter:
    def __init__(self, mergentId, currency):
        self.__value = '{0}{1}'.format(currency.unit, mergentId)

    def minus(self):
        return '-'+self.__value

    def __str__(self):
        return self.__value
