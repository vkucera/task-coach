import datetime

class TimeDelta(datetime.timedelta):
    def hoursMinutesSeconds(self):
        ''' Return a tuple (hours, minutes, seconds). Note that the caller
            is responsible for checking whether the TimeDelta instance is positive
            or negative. '''
        if self < TimeDelta():
            seconds = 3600*24 - self.seconds
            days = abs(self.days) - 1
        else:
            seconds = self.seconds
            days = self.days
        hours, seconds = seconds/3600, seconds%3600
        minutes, seconds = seconds/60, seconds%60
        hours += days*24
        return hours, minutes, seconds
        
    def __add__(self, other):
        ''' Make sure we return a TimeDelta instance and not a datetime.timedelta instance '''
        sum = super(TimeDelta, self).__add__(other)
        return self.__class__(sum.days, sum.seconds, sum.microseconds)
        
    def __sub__(self, other):
        result = super(TimeDelta, self).__sub__(other)
        return self.__class__(result.days, result.seconds, result.microseconds)
        
oneDay = TimeDelta(days=1)
oneYear = TimeDelta(days=365)

def parseTimeDelta(string):
    try:
        hours, minutes, seconds = [int(x) for x in string.split(':')]
    except ValueError:
        hours, minutes, seconds = 0, 0, 0 
    return TimeDelta(hours=hours, minutes=minutes, seconds=seconds)
    