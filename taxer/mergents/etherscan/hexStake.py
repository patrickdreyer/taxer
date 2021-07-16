class HEXStake:
    def __init__(self, principal, interest, total):
        self.__principal = HEXStake.__clean(principal)
        self.__interest = HEXStake.__clean(interest)
        self.__total = HEXStake.__clean(total)

    @property
    def principal(self):
        return self.__principal

    @property
    def interest(self):
        return self.__interest

    @property
    def total(self):
        return self.__total

    @staticmethod
    def __clean(values):
        value = ''.join(values)
        return float(str.replace(value, ',', ''))
