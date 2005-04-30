import wx, task, meta

class IOController(object): 
    def __init__(self, taskFile, messageCallback): 
        super(IOController, self).__init__()
        self.__taskFile = taskFile
        self.__messageCallback = messageCallback
        self.__fileDialogOpts = { 'default_path' : '.', 
            'default_extension' : 'tsk', 'wildcard' : 
            '%s files (*.tsk)|*.tsk|XML files (*.xml)|*.xml|All files (*.*)|*'%meta.name }

    def needSave(self):
        return self.__taskFile.needSave()
        
    def displayMessage(self, verb, file, toorfrom=None):
        if toorfrom:
            nrTasks = len(file)
            message = u'%s %d task%s %s %s'%(verb, nrTasks, 
                nrTasks != 1 and 's' or '', toorfrom, file)
        else:
            message = u'%s %s'%(verb, file)
        self.__messageCallback(message)

    def open(self, filename=None, showerror=wx.MessageBox, *args):
        if not self.close():
            return
        if not filename:
            filename = wx.FileSelector("Open", **self.__fileDialogOpts)
        if filename:
            self.__taskFile.setFilename(filename)
            try:
                self.__taskFile.load()
                self.displayMessage('Loaded', self.__taskFile, 'from')
            except:
                self.__taskFile.setFilename('')
                showerror("Error while reading %s.\n" 
                    "Are you sure it is a %s-file?"%(filename, meta.name), 
                    caption="File error", style=wx.ICON_ERROR)

    def merge(self, filename=None):
        if not filename:
            filename = wx.FileSelector('Merge', **self.__fileDialogOpts)
        if filename:
            self.__taskFile.merge(filename)
            self.displayMessage('Merged', filename) 

    def save(self, *args):
        if self.__taskFile.filename():
            self.__taskFile.save()
            self.displayMessage('Saved', self.__taskFile, 'to')
            return True
        elif len(self.__taskFile) > 0:
            return self.saveas()
        else:
            return False

    def saveas(self):
        filename = wx.FileSelector("Save as...", flags=wx.SAVE, **self.__fileDialogOpts)
        if filename:
            self.__taskFile.saveas(filename)
            self.displayMessage('Saved', self.__taskFile, 'to')
            return True
        else:
            return False

    def saveselection(self, tasks, filename=None):
        if not filename:
            filename = wx.FileSelector("Save as...", flags=wx.SAVE, **self.__fileDialogOpts)
        if filename:
            selectionFile = task.TaskFile(filename)
            selectionFile.extend(tasks)
            selectionFile.save()
            self.displayMessage('Saved', selectionFile, 'to')        
        
    def close(self):
        if self.__taskFile.needSave():
            result = wx.MessageBox('You have unsaved changes.\n'
                'Save before closing?', '%s: save changes?'%meta.name,
                wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
            if result == wx.YES:
                if not self.save():
                    return False
            elif result == wx.CANCEL:
                return False
        self.displayMessage('Closed', file=self.__taskFile.filename())
        self.__taskFile.close()
        import patterns
        patterns.CommandHistory().clear()
        return True
