class Transaction:
    def __init__(self, mergentId, dateTime, id, note=''):
        self.__mergentId = mergentId
        self.__dateTime = dateTime
        self.__id = id
        self.__note = note

    @property
    def mergentId(self):
        return self.__mergentId

    @property
    def dateTime(self):
        return self.__dateTime

    @property
    def id(self):
        return self.__id

    @property
    def note(self):
        return self.__note
