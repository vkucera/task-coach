import wx, task, patterns, meta


class IOController(patterns.Observable):
    def __init__(self, app, taskFile, effortList, settings): 
        super(IOController, self).__init__()
        self.taskFile = taskFile
        self._effortList = effortList
        self.app = app # FIXME: pass displayMessage method instead of app object
        self.settings = settings
        self.fileDialogOpts = { 'default_path' : '.', 
            'default_extension' : 'tsk', 'wildcard' : 
            '%s files (*.tsk)|*.tsk|All files (*.*)|*'%meta.name }

    def filename(self):
        return self.taskFile.filename()

    def displayMessage(self, verb, file, toorfrom=None):
        if toorfrom:
            nrTasks = len(file)
            message = '%s %d task%s %s %s'%(verb, nrTasks, 
                nrTasks != 1 and 's' or '', toorfrom, file)
        else:
            message = '%s %s'%(verb, file)
        self.app.displayMessage(message)

    def open(self, filename=None, showerror=wx.MessageBox, *args):
        if not self.close():
            return
        if not filename:
            filename = wx.FileSelector("Open", **self.fileDialogOpts)
        if filename:
            self.taskFile.setFilename(filename)
            try:
                self.taskFile.load()
                self.displayMessage('Loaded', self.taskFile, 'from')
            except:
                self.taskFile.setFilename('')
                showerror("Error while reading %s.\n" 
                    "Are you sure it is a %s-file?"%(filename, meta.name), 
                    caption="File error", style=wx.ICON_ERROR)
            self._notifyObserversOfChange()

    def merge(self, filename=None):
        if not filename:
            filename = wx.FileSelector('Merge', **self.fileDialogOpts)
        if filename:
            self.taskFile.merge(filename)
            self.displayMessage('Merged', filename) 

    def save(self, *args):
        if self.taskFile:
            self.taskFile.save()
            self.displayMessage('Saved', self.taskFile, 'to')
            return True
        elif len(self.taskFile) > 0:
            return self.saveas()
        else:
            return False

    def saveas(self):
        filename = wx.FileSelector("Save as...", flags=wx.SAVE, **self.fileDialogOpts)
        if filename:
            self.taskFile.saveas(filename)
            self.displayMessage('Saved', self.taskFile, 'to')
            self._notifyObserversOfChange()
            return True
        else:
            return False

    def saveselection(self, tasks, filename=None):
        if not filename:
            filename = wx.FileSelector("Save as...", flags=wx.SAVE, **self.fileDialogOpts)
        if filename:
            selectionFile = task.TaskFile(self._effortList, filename)
            selectionFile.extend(tasks)
            selectionFile.save()
            self.displayMessage('Saved', selectionFile, 'to')

    def exportToXML(self):
        self.fileDialogOpts['default_extension'] = 'xml'
        self.fileDialogOpts['wildcard'] = 'XML files (*.xml)|*.xml|' + self.fileDialogOpts['wildcard']
        filename = wx.FileSelector("Export to XML...", flags=wx.SAVE, **self.fileDialogOpts)
        if filename:
            self.taskFile.exportToXML(filename)
            self.displayMessage('Exported', filename, 'to')

        
    def close(self):
        if self.taskFile.needSave():
            result = wx.MessageBox('You have unsaved changes.\n'
                'Save before closing?', 'Save changes?',
                wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
            if result == wx.YES:
                if not self.save():
                    return False
            elif result == wx.CANCEL:
                return False
        self.displayMessage('Closed', file=self.taskFile.filename())
        self.taskFile.close()
        patterns.CommandHistory().clear()
        self._notifyObserversOfChange()
        return True

    def quit(self, *args):
        self.settings.set('file', 'lastfile', self.taskFile.filename())
        return self.close()

