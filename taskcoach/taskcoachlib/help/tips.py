import wx, meta
from i18n import _

tips = [
_('''%(name)s has a mailinglist where you can discuss usage of %(name)s with fellow users, discuss and request features and complain about bugs. Go to %(url)s and join today!''')%meta.metaDict, 
_('''%(name)s has unlimited undo and redo. Any change that you make, be it editing a task description, or deleting an effort record, is undoable. Select 'Edit' -> 'Undo' and 'Edit' -> 'Redo' to go backwards and forwards through your edit history.''')%meta.metaDict, 
_('''%(name)s is available in a number of different languages. Select 'Edit' -> 'Preferences' to see whether your language is one of them. If your language is not available or the translation needs improvement, please consider helping with the translation of %(name)s. Visit %(url)s for more information about how you can help.''')%meta.metaDict,
_('''If you enter a URL (e.g. %(url)s) in a task or effort description, it becomes a link. Clicking on the link will open the URL in your default web browser.''')%meta.metaDict,
_('''You can drag and drop tasks in the tree view to rearrange parent-child relationships between tasks. The same goes for categories.'''),
_('''You can drag files from a file browser onto a task to create attachments. Dragging the files over a tab will raise the appropriate page, dragging the files over a collapsed task (the boxed + sign) in the tree view will expand the task to show its subtasks.'''),
_('''You can create any viewer layout you want by dragging and dropping the tabs. Unfortunately, due to a limitation of the current version of the graphical toolkit (wxPython), the layout cannot be saved for reuse in the next session.'''),
_('''What is actually printed when you select 'File' -> 'Print' depends on the current view. If the current view shows the task list, a list of tasks will be printed, if the current view shows effort grouped by month, that will be printed. The same goes for visible columns, sort order, filtered tasks, etc.'''),
_('''Left-click a column header to sort by that column. Click the column header again to change the sort order from ascending to descending and back again. Right-click a column header to hide that column or make additional columns visible.''')
]


class TipProvider(wx.PyTipProvider):
    def __init__(self, tipIndex):
        super(TipProvider, self).__init__(tipIndex)
        self.__tipIndex = tipIndex
        
    def GetTip(self):
        tip = tips[self.__tipIndex]
        self.__tipIndex += 1
        if self.__tipIndex >= len(tips):
            self.__tipIndex = 0
        return tip
    
    def GetCurrentTip(self):
        return self.__tipIndex

        
def showTips(parent, settings):
    tipProvider = TipProvider(settings.getint('window', 'tipsindex'))
    keepShowingTips = wx.ShowTip(parent, tipProvider)
    settings.set('window', 'tips', str(keepShowingTips))
    settings.set('window', 'tipsindex', str(tipProvider.GetCurrentTip()))
