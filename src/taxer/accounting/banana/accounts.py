class BananaAccounts:
    def __init__(self, config):
        self.__config = config

    @property
    def transfer(self):
        return self.__config['transfer']

    @property
    def equity(self):
        return self.__config['equity']

    @property
    def fees(self):
        return self.__config['fees']

    @property
    def staked(self):
        return self.__config['staked']

    def get(self, unit, mergentId):
        u = self.__config['map'][unit]
        m = u[mergentId]
        return m
