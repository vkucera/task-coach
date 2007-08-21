import datetime, timedelta, re

class DateTime(datetime.datetime):
    def weeknumber(self):
        return self.isocalendar()[1]

    def weekday(self):
        return self.isoweekday()
        
    def startOfDay(self):
        return self.replace(hour=0, minute=0, second=0, microsecond=0)
        
    def endOfDay(self):
        return self.replace(hour=23, minute=59, second=59, microsecond=999999)

    def startOfWeek(self):
        days = self.weekday()
        monday = self - timedelta.TimeDelta(days=days-1)
        return DateTime(monday.year, monday.month, monday.day)
        
    def endOfWeek(self):
        days = self.weekday()
        sunday = self + timedelta.TimeDelta(days=7-days)
        return DateTime(sunday.year, sunday.month, sunday.day).endOfDay()
        
    def startOfMonth(self):
        return DateTime(self.year, self.month, 1)
        
    def endOfMonth(self):
        for lastday in [31,30,29,28]:
            try:
                return DateTime(self.year, self.month, lastday).endOfDay()
            except ValueError:
                pass
                
    def __sub__(self, other):
        ''' Make sure substraction returns a TimeDelta and not a datetime.timedelta '''
        result = super(DateTime, self).__sub__(other)
        if isinstance(result, datetime.timedelta):
            result = timedelta.TimeDelta(result.days, result.seconds, result.microseconds)
        return result

    def __add__(self, other):
        result = super(DateTime, self).__add__(other)
        return self.__class__(result.year, result.month, result.day, 
            result.hour, result.minute, result.second, result.microsecond)


def parseDateTime(string):
    if string in ('', 'None'):
        return None
    else:
        args = [int(arg) for arg in re.split('[-:. ]', string)]
        return DateTime(*args)
        
        