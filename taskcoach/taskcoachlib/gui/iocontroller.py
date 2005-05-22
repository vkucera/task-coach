import wx, task, meta
from i18n import _

class IOController(object): 
    def __init__(self, taskFile, messageCallback): 
        super(IOController, self).__init__()
        self.__taskFile = taskFile
        self.__messageCallback = messageCallback
        self.__fileDialogOpts = { 'default_path' : '.', 
            'default_extension' : 'tsk', 'wildcard' : 
            _('%s files (*.tsk)|*.tsk|XML files (*.xml)|*.xml|All files (*.*)|*')%meta.name }

    def needSave(self):
        return self.__taskFile.needSave()
        
    def open(self, filename=None, showerror=wx.MessageBox, *args):
        if not self.close():
            return
        if not filename:
            filename = wx.FileSelector(_('Open'), **self.__fileDialogOpts)
        if filename:
            self.__taskFile.setFilename(filename)
            try:
                self.__taskFile.load()
                self.__messageCallback(_('Loaded %(nrtasks)d tasks from %(filename)s')%{'nrtasks': len(self.__taskFile), 'filename': self.__taskFile.filename()})
            except:
                self.__taskFile.setFilename('')
                showerror(_('Error while reading %s.\n' 
                    'Are you sure it is a %s-file?')%(filename, meta.name), 
                    caption=_('File error'), style=wx.ICON_ERROR)

    def merge(self, filename=None):
        if not filename:
            filename = wx.FileSelector(_('Merge'), **self.__fileDialogOpts)
        if filename:
            self.__taskFile.merge(filename)
            self.__messageCallback(_('Merged %(filename)s')%{'filename': filename}) 

    def save(self, *args):
        if self.__taskFile.filename():
            self.__taskFile.save()
            self.__messageCallback(_('Saved %(nrtasks)d tasks to %(filename)s')%{'nrtasks': len(self.__taskFile), 'filename': self.__taskFile.filename()})
            return True
        elif len(self.__taskFile) > 0:
            return self.saveas()
        else:
            return False

    def saveas(self):
        filename = wx.FileSelector(_('Save as...'), flags=wx.SAVE, **self.__fileDialogOpts)
        if filename:
            self.__taskFile.saveas(filename)
            self.__messageCallback(_('Saved %(nrtasks)d tasks to %(filename)s')%{'nrtasks': len(self.__taskFile), 'filename': filename})
            return True
        else:
            return False

    def saveselection(self, tasks, filename=None):
        if not filename:
            filename = wx.FileSelector(_('Save as...'), flags=wx.SAVE, **self.__fileDialogOpts)
        if filename:
            selectionFile = task.TaskFile(filename)
            selectionFile.extend(tasks)
            selectionFile.save()
            self.__messageCallback(_('Saved %(nrtasks)d tasks to %(filename)s')%{'nrtasks': len(selectionFile), 'filename': filename})
        
    def close(self):
        if self.__taskFile.needSave():
            result = wx.MessageBox(_('You have unsaved changes.\n'
                'Save before closing?'), _('%s: save changes?')%meta.name,
                wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
            if result == wx.YES:
                if not self.save():
                    return False
            elif result == wx.CANCEL:
                return False
        self.__messageCallback(_('Closed %s')%self.__taskFile.filename())
        self.__taskFile.close()
        import patterns
        patterns.CommandHistory().clear()
        return True
