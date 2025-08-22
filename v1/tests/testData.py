from datetime import datetime
import json
import pathlib


class TestData:
    @staticmethod
    def loadJson(scriptPath: str, fileName: str):
        return json.load(open(pathlib.Path(scriptPath).parent.resolve() / f"{fileName}.json"), object_hook=TestData.__objectHook)
    
    @staticmethod
    def __objectHook(obj):
        if 'dateTime' in obj:
            obj['dateTime'] = datetime.fromisoformat(obj['dateTime'])
        return obj
