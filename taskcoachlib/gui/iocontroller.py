import wx, meta, os, codecs, persistence
from i18n import _
import domain.task as task

class IOController(object): 
    ''' IOController is responsible for opening, closing, loading,
    saving, and exporting files. It also presents the necessary dialogs
    to let the user specify what file to load/save/etc.'''

    def __init__(self, taskFile, messageCallback, settings): 
        super(IOController, self).__init__()
        self.__taskFile = taskFile
        self.__messageCallback = messageCallback
        self.__settings = settings
        self.__tskFileDialogOpts = {'default_path' : os.getcwd(), 
            'default_extension' : 'tsk', 'wildcard' : 
            _('%s files (*.tsk)|*.tsk|XML files (*.xml)|*.xml|All files (*.*)|*')%meta.name }
        self.__icsFileDialogOpts = {'default_path' : os.getcwd(), 
            'default_extension' : 'ics', 'wildcard' : 
            _('iCalendar files (*.ics)|*.ics|All files (*.*)|*') }

    def needSave(self):
        return self.__taskFile.needSave()
        
    def open(self, filename=None, showerror=wx.MessageBox, *args):
        if not self.close():
            return
        if not filename:
            filename = self.__askUserForFile(_('Open'))
        if filename:
            self.__taskFile.setFilename(filename)
            try:
                self.__taskFile.load()                
            except:
                self.__taskFile.setFilename('')
                showerror(_('Error while reading %s.\n' 
                    'Are you sure it is a %s-file?')%(filename, meta.name), 
                    caption=_('File error'), style=wx.ICON_ERROR)
                return
            self.__messageCallback(_('Loaded %(nrtasks)d tasks from %(filename)s')%{'nrtasks': len(self.__taskFile), 'filename': self.__taskFile.filename()})
            self.__addRecentFile(filename)
            
    def merge(self, filename=None):
        if not filename:
            filename = self.__askUserForFile(_('Merge'))
        if filename:
            self.__taskFile.merge(filename)
            self.__messageCallback(_('Merged %(filename)s')%{'filename': filename}) 
            self.__addRecentFile(filename)

    def save(self, *args):
        if self.__taskFile.filename():
            self.__taskFile.save()
            self.__messageCallback(_('Saved %(nrtasks)d tasks to %(filename)s')%{'nrtasks': len(self.__taskFile), 'filename': self.__taskFile.filename()})
            return True
        elif len(self.__taskFile) > 0:
            return self.saveas()
        else:
            return False

    def saveas(self, filename=None):
        if not filename:
            filename = self.__askUserForFile(_('Save as...'), flags=wx.SAVE)
        if filename:
            self.__taskFile.saveas(filename)
            self.__messageCallback(_('Saved %(nrtasks)d tasks to %(filename)s')%{'nrtasks': len(self.__taskFile), 'filename': filename})
            self.__addRecentFile(filename)
            return True
        else:
            return False

    def saveselection(self, tasks, filename=None):
        if not filename:
            filename = self.__askUserForFile(_('Save as...'), flags=wx.SAVE)
        if filename:
            selectionFile = persistence.TaskFile(filename)
            selectionFile.extend(tasks)
            selectionFile.save()
            self.__messageCallback(_('Saved %(nrtasks)d tasks to %(filename)s')%{'nrtasks': len(selectionFile), 'filename': filename})
            self.__addRecentFile(filename)
        
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

    def exportAsICS(self, filename=None):
        if not filename:
            filename = self.__askUserForFile(_('Export as iCalendar...'),
                flags=wx.SAVE, fileDialogOpts=self.__icsFileDialogOpts)
        if filename:
            icsFile = codecs.open(filename, 'w', 'utf-8')
            persistence.ICSWriter(icsFile).write(self.__taskFile)
            icsFile.close()
            self.__messageCallback(_('Exported %(nrtasks)d tasks to %(filename)s')%{'nrtasks': len(self.__taskFile), 'filename': filename})
            return True
        else:
            return False

    def __addRecentFile(self, fileName):
        recentFiles = eval(self.__settings.get('file', 'recentfiles'))
        if fileName in recentFiles:
            recentFiles.remove(fileName)
        recentFiles.insert(0, fileName)
        maximumNumberOfRecentFiles = self.__settings.getint('file', 'maxrecentfiles')
        recentFiles = recentFiles[:maximumNumberOfRecentFiles]
        self.__settings.set('file', 'recentfiles', str(recentFiles))
        
    def __askUserForFile(self, title, fileDialogOpts=None, flags=wx.OPEN):
        fileDialogOpts = fileDialogOpts or self.__tskFileDialogOpts
        return wx.FileSelector(title, flags=flags, **fileDialogOpts)
