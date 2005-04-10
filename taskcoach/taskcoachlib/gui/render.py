''' render.py - functions to render various objects, like dates, task
subjects, etc. '''

taskSeparator = ' -> '

def date(date):
    ''' render a date (of type date.Date) '''
    return str(date)

def subject(task, recursively=False, sep=taskSeparator):
    ''' render a task subject '''
    prefix = ''
    if recursively and task.parent():
        prefix = subject(task.parent(), recursively) + sep 
    return prefix + task.subject()
   
def daysLeft(timeLeft):
    ''' render time left (of type date.TimeDelta) in days '''
    import date
    if timeLeft == date.TimeDelta.max:
        return 'Infinite'
    else:
        return str(timeLeft.days)

def timeSpent(timeSpent):
    ''' render time spent (of type date.TimeDelta) as
    "<hours>:<minutes>:<seconds>" '''
    return '%d:%02d:%02d'%timeSpent.hoursMinutesSeconds()
    
def budget(aBudget):
    ''' render budget (of type date.TimeDelta) as
    "<hours>:<minutes>:<seconds>" or "None" if budget is infinite. '''
    import date
    if aBudget == date.TimeDelta.max:
        return 'None'
    else:
        return timeSpent(aBudget)
        
def dateTime(dateTime):
    return dateTime.strftime('%Y-%m-%d %H:%M')
    
def dateTimePeriod(start, stop):
    if stop is None:
        return '%s - now'%dateTime(start)
    elif start.date() == stop.date():
        return '%s %s - %s'%(date(start.date()), time(start), time(stop))
    else:
        return '%s - %s'%(dateTime(start), dateTime(stop))
            
def time(dateTime):
    return dateTime.strftime('%H:%M')
    
def month(dateTime):
    return dateTime.strftime('%Y %B')
    
def weekNumber(dateTime):
    # Would have liked to use dateTime.strftime('%Y-%U'), but the week number is one off
    # in 2004
    return '%d-%d'%(dateTime.year, dateTime.weeknumber())
    
