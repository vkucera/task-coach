import wx

def taskColor(task):
    if task.completed():
        return wx.GREEN
    elif task.overdue(): 
        return wx.RED
    elif task.dueToday():
        #return wx.NamedColour('GOLD')
        return wx.Colour(red=255, green=128, blue=0)
    elif task.inactive(): 
        return wx.NamedColour('LIGHT GREY')
    else:
        return wx.BLACK
