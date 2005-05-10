import datetime

class Time(datetime.time):
    @classmethod
    def now(cls):
        d = datetime.datetime.now()
        return cls(d.hour, d.minute, d.second, d.microsecond)