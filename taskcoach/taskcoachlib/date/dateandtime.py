import datetime

class DateTime(datetime.datetime):
    def weeknumber(self):
        return self.isocalendar()[1]