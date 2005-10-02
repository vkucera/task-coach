import wx

def taskColor(task, settings):
    if task.completed():
        setting = 'completedtasks'
    elif task.overdue(): 
        setting = 'overduetasks'
    elif task.dueToday():
        setting = 'duetodaytasks'
    elif task.inactive(): 
        setting = 'inactivetasks'
    else:
        setting = 'activetasks'
    return wx.Colour(*eval(settings.get('color', setting)))