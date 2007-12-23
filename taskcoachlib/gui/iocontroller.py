import wx, os, sys, codecs, traceback
import meta, persistence
from i18n import _
from domain import task

class IOController(object): 
    ''' IOController is responsible for opening, closing, loading,
    saving, and exporting files. It also presents the necessary dialogs
    to let the user specify what file to load/save/etc.'''

    def __init__(self, taskFile, messageCallback, settings): 
        super(IOController, self).__init__()
        self.__taskFile = taskFile
        self.__messageCallback = messageCallback
        self.__settings = settings
        self.__tskFileDialogOpts = {'default_path': os.getcwd(), 
            'default_extension': 'tsk', 'wildcard': 
            _('%s files (*.tsk)|*.tsk|XML files (*.xml)|*.xml|All files (*.*)|*')%meta.name }
        self.__icsFileDialogOpts = {'default_path': os.getcwd(), 
            'default_extension': 'ics', 'wildcard': 
            _('iCalendar files (*.ics)|*.ics|All files (*.*)|*') }
        self.__htmlFileDialogOpts = {'default_path': os.getcwd(), 
            'default_extension': 'html', 'wildcard': 
            _('HTML files (*.html)|*.html|All files (*.*)|*') }
        self.__csvFileDialogOpts = {'default_path': os.getcwd(),
            'default_extension': 'csv', 'wildcard': 
            _('CSV files (*.csv)|*.csv|Text files (*.txt)|*.txt|All files (*.*)|*')}

    def needSave(self):
        return self.__taskFile.needSave()
        
    def open(self, filename=None, showerror=wx.MessageBox, 
             fileExists=os.path.exists, *args):
        errorMessageOptions = dict(caption=_('%s file error')%meta.name, 
                                   style=wx.ICON_ERROR)
        if self.__taskFile.needSave():
            if not self.__saveUnsavedChanges():
                return
        if not filename:
            filename = self.__askUserForFile(_('Open'))
        if not filename:
            return
        if fileExists(filename):
            self.__closeUnconditionally() 
            self.__taskFile.setFilename(filename)
            try:
                self.__taskFile.load()                
            except Exception:
                self.__taskFile.setFilename('')
                showerror(_('Error while reading %s:\n')%filename + \
                    ''.join(traceback.format_exception(*sys.exc_info())) + \
                    _('Are you sure it is a %s-file?')%meta.name, 
                    **errorMessageOptions)
                return
            self.__messageCallback(_('Loaded %(nrtasks)d tasks from %(filename)s')%{'nrtasks': len(self.__taskFile), 'filename': self.__taskFile.filename()})
            self.__addRecentFile(filename)
        else:
            showerror(_("Cannot open %s because it doesn't exist")%filename,
                      **errorMessageOptions)
            self.__removeRecentFile(filename)
            
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
            if not self.__saveUnsavedChanges():
                return False
        self.__closeUnconditionally()
        return True

    def exportAsICS(self, filename=None):
        if not filename:
            filename = self.__askUserForFile(_('Export as iCalendar...'),
                flags=wx.SAVE, fileDialogOpts=self.__icsFileDialogOpts)
        if filename:
            icsFile = self.__openFileForWriting(filename)
            persistence.ICSWriter(icsFile).write(self.__taskFile)
            icsFile.close()
            self.__messageCallback(_('Exported %(nrtasks)d tasks to %(filename)s')%{'nrtasks': len(self.__taskFile), 'filename': filename})
            return True
        else:
            return False

    def exportAsHTML(self, viewer, filename=None):
        if not filename:
            filename = self.__askUserForFile(_('Export as HTML...'),
                flags=wx.SAVE, fileDialogOpts=self.__htmlFileDialogOpts)
        if filename:
            htmlFile = self.__openFileForWriting(filename)
            persistence.HTMLWriter(htmlFile).write(viewer)
            htmlFile.close()
            self.__messageCallback(_('Exported %(nrtasks)d items to %(filename)s')%{'nrtasks': viewer.size(), 'filename': filename})
            return True
        else:
            return False

    def exportAsCSV(self, viewer, filename=None):
        if not filename:
            filename = self.__askUserForFile(_('Export as CSV...'),
                flags=wx.SAVE, fileDialogOpts=self.__csvFileDialogOpts)
        if filename:
            csvFile = self.__openFileForWriting(filename)
            persistence.CSVWriter(csvFile).write(viewer)
            csvFile.close()
            self.__messageCallback(_('Exported %(nrtasks)d items to %(filename)s')%{'nrtasks': viewer.size(), 'filename': filename})
            return True
        else:
            return False
        
    def __openFileForWriting(self, filename, mode='w', encoding='utf-8'):
        return codecs.open(filename, mode, encoding)
        
    def __addRecentFile(self, fileName):
        recentFiles = self.__settings.getlist('file', 'recentfiles')
        if fileName in recentFiles:
            recentFiles.remove(fileName)
        recentFiles.insert(0, fileName)
        maximumNumberOfRecentFiles = self.__settings.getint('file', 'maxrecentfiles')
        recentFiles = recentFiles[:maximumNumberOfRecentFiles]
        self.__settings.setlist('file', 'recentfiles', recentFiles)
        
    def __removeRecentFile(self, fileName):
        recentFiles = self.__settings.getlist('file', 'recentfiles')
        if fileName in recentFiles:
            recentFiles.remove(fileName)
            self.__settings.setlist('file', 'recentfiles', recentFiles)
        
    def __askUserForFile(self, title, fileDialogOpts=None, flags=wx.OPEN):
        fileDialogOpts = fileDialogOpts or self.__tskFileDialogOpts
        return wx.FileSelector(title, flags=flags, **fileDialogOpts)

    def __saveUnsavedChanges(self):
        result = wx.MessageBox(_('You have unsaved changes.\n'
            'Save before closing?'), _('%s: save changes?')%meta.name,
            wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
        if result == wx.YES:
            if not self.save():
                return False
        elif result == wx.CANCEL:
            return False
        return True
    
    def __closeUnconditionally(self):
        self.__messageCallback(_('Closed %s')%self.__taskFile.filename())
        self.__taskFile.close()
        import patterns
        patterns.CommandHistory().clear()
        
