import inspect


class Container():
    def __init__(self):
        self.__dict = dict[str, object]()

    def __setitem__(self, key:str, value:object):
        self.__dict[key] = value

    def __getitem__(self, key:str) -> object:
        value = self.__dict[key]
        if inspect.isfunction(value):
            value = self.__dict[key](self)
            self.__dict[key] = value
        return value
