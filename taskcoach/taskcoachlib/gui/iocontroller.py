'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import wx, os, sys, codecs, traceback
from taskcoachlib import meta, persistence
from taskcoachlib.i18n import _
from taskcoachlib.domain import task
from taskcoachlib.syncml import sync
from taskcoachlib.widgets import conflict

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
            _('%s files (*.tsk)|*.tsk|Backup files (*.tsk.bak)|*.tsk.bak|All files (*.*)|*')%meta.name }
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
    
    def openAfterStart(self, commandLineArgs):
        ''' Open either the file specified on the command line, or the file
            the user was working on previously, or none at all. '''
        if commandLineArgs:
            filename = commandLineArgs[0].decode(sys.getfilesystemencoding())
        else:
            filename = self.__settings.get('file', 'lastfile')
        if filename:
            self.open(filename)
            
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
            self.__messageCallback(_('Loaded %(nrtasks)d tasks from %(filename)s')%\
                {'nrtasks': len(self.__taskFile.tasks()), 
                 'filename': self.__taskFile.filename()})
            self.__addRecentFile(filename)
        else:
            errorMessage = _("Cannot open %s because it doesn't exist")%filename
            # Use CallAfter on Mac OSX because otherwise the app will hang:
            if '__WXMAC__' in wx.PlatformInfo:
                wx.CallAfter(showerror, errorMessage, **errorMessageOptions)
            else:
                showerror(errorMessage, **errorMessageOptions)
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
            self.__showSaveMessage(self.__taskFile)
            return True
        elif not self.__taskFile.isEmpty():
            return self.saveas()
        else:
            return False

    def saveas(self, filename=None):
        if not filename:
            filename = self.__askUserForFile(_('Save as...'), flags=wx.SAVE)
        if filename:
            self.__taskFile.saveas(filename)
            self.__showSaveMessage(self.__taskFile)
            self.__addRecentFile(filename)
            return True
        else:
            return False

    def saveselection(self, tasks, filename=None):
        if not filename:
            filename = self.__askUserForFile(_('Save as...'), flags=wx.SAVE)
        if filename:
            selectionFile = persistence.TaskFile(filename)
            selectionFile.tasks().extend(tasks)
            selectionFile.save()
            self.__showSaveMessage(selectionFile)        
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
            persistence.ICSWriter(icsFile).write(self.__taskFile.tasks())
            icsFile.close()
            self.__messageCallback(_('Exported %(nrtasks)d tasks to %(filename)s')%\
                {'nrtasks': len(self.__taskFile.tasks()), 'filename': filename})
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
            self.__messageCallback(_('Exported %(nrtasks)d items to %(filename)s')%\
                {'nrtasks': viewer.size(), 'filename': filename})
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
            self.__messageCallback(_('Exported %(nrtasks)d items to %(filename)s')%\
                {'nrtasks': viewer.size(), 'filename': filename})
            return True
        else:
            return False
        
    def synchronize(self, password):
        synchronizer = sync.Synchronizer(self.__settings.get('syncml', 'preferredsyncmode'),
                                         self.__settings.getboolean('syncml', 'verbose'),
                                         self.__settings.get('syncml', 'client'),
                                         self.__syncReport, self, self.__taskFile,
                                         self.__settings.get('syncml', 'url'),
                                         self.__settings.get('syncml', 'username'),
                                         password,
                                         self.__settings.get('syncml', 'taskdbname'),
                                         self.__settings.getboolean('syncml', 'synctasks'),
                                         self.__settings.get('syncml', 'notedbname'),
                                         self.__settings.getboolean('syncml', 'syncnotes'))
        try:
            synchronizer.synchronize()
        finally:
            synchronizer.Destroy()

        self.__messageCallback(_('Synchronization over.'))

    def resolveNoteConflict(self, flags, local, remote):
        dlg = conflict.ConflictDialog(conflict.NoteConflictPanel,
                                      flags, local, remote,
                                      None, wx.ID_ANY, _('Note conflict'))
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()

        return dlg.resolved

    def resolveTaskConflict(self, flags, local, remote):
        dlg = conflict.ConflictDialog(conflict.TaskConflictPanel,
                                      flags, local, remote,
                                      None, wx.ID_ANY, _('Task conflict'))
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()

        return dlg.resolved

    def __syncReport(self, msg):
        wx.MessageBox(msg, _('Synchronization status'), style=wx.OK|wx.ICON_ERROR)

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
        from taskcoachlib import patterns
        patterns.CommandHistory().clear()
    
    def __showSaveMessage(self, savedFile):    
        self.__messageCallback(_('Saved %(nrtasks)d tasks to %(filename)s')%\
            {'nrtasks': len(savedFile.tasks()), 
             'filename': savedFile.filename()})

