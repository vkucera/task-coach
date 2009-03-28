'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
Copyright (C) 2008 Jerome Laheurte <fraca7@free.fr>

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

import wx, os, sys, codecs, traceback, shutil
from taskcoachlib import meta, persistence
from taskcoachlib.i18n import _
from taskcoachlib.domain import task
from taskcoachlib.thirdparty import lockfile

try:
    from taskcoachlib.syncml import sync
    from taskcoachlib.widgets import conflict
except ImportError:
    # Unsupported platform.
    pass


class IOController(object): 
    ''' IOController is responsible for opening, closing, loading,
    saving, and exporting files. It also presents the necessary dialogs
    to let the user specify what file to load/save/etc.'''

    def __init__(self, taskFile, messageCallback, settings): 
        super(IOController, self).__init__()
        self.__taskFile = taskFile
        self.__messageCallback = messageCallback
        self.__settings = settings
        defaultPath = os.path.expanduser('~')
        self.__tskFileDialogOpts = {'default_path': defaultPath, 
            'default_extension': 'tsk', 'wildcard': 
            _('%s files (*.tsk)|*.tsk|Backup files (*.tsk.bak)|*.tsk.bak|All files (*.*)|*')%meta.name }
        self.__icsFileDialogOpts = {'default_path': defaultPath, 
            'default_extension': 'ics', 'wildcard': 
            _('iCalendar files (*.ics)|*.ics|All files (*.*)|*') }
        self.__htmlFileDialogOpts = {'default_path': defaultPath, 
            'default_extension': 'html', 'wildcard': 
            _('HTML files (*.html)|*.html|All files (*.*)|*') }
        self.__csvFileDialogOpts = {'default_path': defaultPath,
            'default_extension': 'csv', 'wildcard': 
            _('CSV files (*.csv)|*.csv|Text files (*.txt)|*.txt|All files (*.*)|*')}
        self.__vcalFileDialogOpts = {'default_path': defaultPath, 
            'default_extension': 'vcal', 'wildcard': 
            _('VCalendar files (*.vcal)|*.vcal|All files (*.*)|*') }
        self.__errorMessageOptions = dict(caption=_('%s file error')%meta.name, 
                                          style=wx.ICON_ERROR)

    def syncMLConfig(self):
        return self.__taskFile.syncMLConfig()

    def setSyncMLConfig(self, config):
        self.__taskFile.setSyncMLConfig(config)

    def needSave(self):
        return self.__taskFile.needSave()

    def hasDeletedItems(self):
        return bool([task for task in self.__taskFile.tasks() if task.isDeleted()] + \
                    [note for note in self.__taskFile.notes() if note.isDeleted()])

    def purgeDeletedItems(self):
        self.__taskFile.tasks().removeItems([task for task in self.__taskFile.tasks() if task.isDeleted()])
        self.__taskFile.notes().removeItems([note for note in self.__taskFile.notes() if note.isDeleted()])

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
        if self.__taskFile.needSave():
            if not self.__saveUnsavedChanges():
                return
        if not filename:
            filename = self.__askUserForFile(_('Open'))
        if not filename:
            return
        self.__updateDefaultPath(filename)
        if fileExists(filename):
            self.__closeUnconditionally() 
            try:
                self.__taskFile.load(filename)
            except lockfile.AlreadyLocked:
                showerror(_('Cannot open %s because it is locked')%filename, 
                          **self.__errorMessageOptions)
                return
            except Exception:
                showerror(_('Error while reading %s:\n')%filename + \
                    ''.join(traceback.format_exception(*sys.exc_info())) + \
                    _('Are you sure it is a %s-file?')%meta.name, 
                    **self.__errorMessageOptions)
                return
            self.__messageCallback(_('Loaded %(nrtasks)d tasks from %(filename)s')%\
                {'nrtasks': len(self.__taskFile.tasks()), 
                 'filename': self.__taskFile.filename()})
            self.__addRecentFile(filename)
        else:
            errorMessage = _("Cannot open %s because it doesn't exist")%filename
            # Use CallAfter on Mac OS X because otherwise the app will hang:
            if '__WXMAC__' in wx.PlatformInfo:
                wx.CallAfter(showerror, errorMessage, **self.__errorMessageOptions)
            else:
                showerror(errorMessage, **self.__errorMessageOptions)
            self.__removeRecentFile(filename)
            
    def merge(self, filename=None):
        if not filename:
            filename = self.__askUserForFile(_('Merge'))
        if filename:
            self.__taskFile.merge(filename)
            self.__messageCallback(_('Merged %(filename)s')%{'filename': filename}) 
            self.__addRecentFile(filename)

    def save(self, showerror=wx.MessageBox, *args):
        if self.__taskFile.filename():
            if self._saveSave(self.__taskFile, showerror):
                return True
            else:
                return self.saveas(showerror=showerror)
        elif not self.__taskFile.isEmpty():
            return self.saveas(showerror=showerror) # Ask for filename
        else:
            return False

    def saveas(self, filename=None, showerror=wx.MessageBox):
        if not filename:
            filename = self.__askUserForFile(_('Save as...'), flags=wx.SAVE)
            if not filename:
                return False # User didn't enter a filename, cancel save
        if self._saveSave(self.__taskFile, showerror, filename):
            return True
        else:
            return self.saveas(showerror=showerror) # Try again

    def saveselection(self, tasks, filename=None, showerror=wx.MessageBox,
                      TaskFileClass=persistence.TaskFile):
        if not filename:
            filename = self.__askUserForFile(_('Save as...'), flags=wx.SAVE)
            if not filename:
                return False # User didn't enter a filename, cancel save
        selectionFile = self._createSelectionFile(tasks, TaskFileClass)
        if self._saveSave(selectionFile, showerror, filename):
            return True
        else:
            return self.saveselection(tasks, showerror=showerror, 
                                      TaskFileClass=TaskFileClass) # Try again
            
    def _createSelectionFile(self, tasks, TaskFileClass):
        selectionFile = TaskFileClass()
        selectionFile.tasks().extend(tasks)
        allCategories = set()
        for task in tasks:
            allCategories.update(task.categories())
        selectionFile.categories().extend(allCategories)
        return selectionFile
    
    def _saveSave(self, file, showerror, filename=None):
        ''' Save the file and show an error message if saving fails. '''
        try:
            if filename:
                file.saveas(filename)
            else:
                file.save()
                filename = file.filename()
            self.__showSaveMessage(file)
            self.__addRecentFile(filename)
            return True
        except IOError, reason:
            errorMessage = _('Cannot save %s\n%s')%(filename, reason)
            showerror(errorMessage, **self.__errorMessageOptions)
            return False
        
    def saveastemplate(self, task):
        name = wx.GetTextFromUser(_('Please enter the template name.'),
                                  _('Save as template'))
        if name:
            filename = os.path.join(self.__settings.pathToTemplatesDir(),
                                    name + '.tsktmpl')
            writer = persistence.TemplateXMLWriter(codecs.open(filename, 'w', 'utf-8'))
            writer.write(task.copy())

    def addtemplate(self):
        filename = self.__askUserForFile(_('Open template...'),
                      fileDialogOpts={'default_extension': 'tsktmpl',
                                      'wildcard': _('%s template files (*.tsktmpl)|*.tsktmpl')%meta.name },
                                         flags=wx.OPEN)
        if filename:
            shutil.copyfile(filename,
                            os.path.join(self.__settings.pathToTemplatesDir(),
                                         os.path.split(filename)[-1]))

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

    def exportAsHTML(self, viewer, filename=None, selectionOnly=False):
        if not filename:
            filename = self.__askUserForFile(_('Export as HTML...'),
                flags=wx.SAVE, fileDialogOpts=self.__htmlFileDialogOpts)
        if filename:
            htmlFile = self.__openFileForWriting(filename)
            count = persistence.HTMLWriter(htmlFile).write(viewer,
                                                           selectionOnly=selectionOnly)
            htmlFile.close()
            self.__messageCallback(_('Exported %(nrtasks)d items to %(filename)s')%\
                {'nrtasks': count, 'filename': filename})
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
        
    def exportAsVCalendar(self, viewer, filename=None):
        if not filename:
            filename = self.__askUserForFile(_('Export as VCalendar...'),
                flags=wx.SAVE, fileDialogOpts=self.__vcalFileDialogOpts)
        if filename:
            vcalFile = self.__openFileForWriting(filename)
            persistence.VCalendarWriter(vcalFile).write(viewer)
            vcalFile.close()
            self.__messageCallback(_('Exported %(nrtasks)d items to %(filename)s')%\
                {'nrtasks': viewer.size(), 'filename': filename})
            return True
        else:
            return False

    def synchronize(self, password):
        synchronizer = sync.Synchronizer(self.__syncReport, self, 
                                         self.__taskFile, password)
        try:
            synchronizer.synchronize()
        finally:
            synchronizer.Destroy()

        self.__messageCallback(_('Finished synchronization'))

    def resolveNoteConflict(self, flags, local, remote):
        return self.resolveConflict(conflict.NoteConflictPanel, 
                                    flags, local, remote, _('Note conflict'))

    def resolveTaskConflict(self, flags, local, remote):
        return self.resolveConflict(conflict.TaskConflictPanel, 
                                    flags, local, remote, _('Task conflict'))
    
    def resolveConflict(self, panel, flags, local, remote, title):
        dialog = conflict.ConflictDialog(panel, flags, local, remote, None, 
                                         wx.ID_ANY, title)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()
        return dialog.resolved

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
            style=wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION|wx.YES_DEFAULT)
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

    def __updateDefaultPath(self, filename):
        for options in [self.__tskFileDialogOpts, self.__csvFileDialogOpts,
                        self.__icsFileDialogOpts, self.__htmlFileDialogOpts,
                        self.__vcalFileDialogOpts]:
            options['default_path'] = os.path.dirname(filename)

