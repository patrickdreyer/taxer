class Lobby():
    def __init__(self, mergentId, dateTime, id):
        self.__mergentId = mergentId
        self.__dateTime = dateTime
        self.__id = id

    @property
    def mergentId(self):
        return self.__mergentId

    @property
    def dateTime(self):
        return self.__dateTime

    @property
    def id(self):
        return self.__id
