import datetime

class TimeDelta(datetime.timedelta):
    pass
    
oneDay = TimeDelta(days=1)
oneYear = TimeDelta(days=365)