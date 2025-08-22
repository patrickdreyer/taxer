from datetime import datetime

class DateTimeX(datetime):
    def __str__(self):
        return f'{self.year:4}-{self.month:02}-{self.day:02} {self.hour:02}:{self.minute:02}'
