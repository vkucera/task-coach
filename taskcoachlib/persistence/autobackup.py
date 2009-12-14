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

import os, shutil, glob, math
from taskcoachlib import patterns
from taskcoachlib.domain import date
                    

class AutoBackup(patterns.Observer):
    ''' If backups are on, AutoBackup creates a backup copy of the task 
        file before it is overwritten. To prevent the number of backups growing
        indefinitely, AutoBackup removes older backups. '''
        
    def __init__(self, settings, copyfile=shutil.copyfile):
        super(AutoBackup, self).__init__()
        self.__settings = settings
        self.__copyfile = copyfile
        self.registerObserver(self.onTaskFileAboutToSave,
                              eventType='taskfile.aboutToSave')
            
    def onTaskFileAboutToSave(self, event):
        ''' Just before a task file is about to be saved, and backups are on,
            create a backup and remove extraneous backup files. '''
        for taskFile in event.sources():
            if self.needBackup(taskFile):
                self.createBackup(taskFile)
            if self.tooManyBackupFiles(taskFile):
                self.removeExtraneousBackupFiles(taskFile)

    def needBackup(self, taskFile):
        return self.__settings.getboolean('file', 'backup') and taskFile.exists()

    def createBackup(self, taskFile):
        self.__copyfile(taskFile.filename(), self.backupFilename(taskFile))

    def tooManyBackupFiles(self, taskFile, glob=glob.glob):
        return bool(self.extraneousBackupFiles(taskFile, glob))
    
    def removeExtraneousBackupFiles(self, taskFile, remove=os.remove, 
                                    glob=glob.glob):
        for backupFile in self.extraneousBackupFiles(taskFile, glob):
            try:
                remove(backupFile)
            except OSError:
                pass # Ignore errors

    def extraneousBackupFiles(self, taskFile, glob=glob.glob):
        backupFiles = self.backupFiles(taskFile, glob)
        backupFiles.sort()
        backupFiles = backupFiles[1:-1] # Keep oldest and newest
        return backupFiles[self.maxNrOfBackupFiles(taskFile, glob)-2:]

    def maxNrOfBackupFiles(self, taskFile, glob):
        ''' The maximum number of backup files we keep depends on the age of
            the oldest backup file. The older the oldest backup file (that is
            never removed), the more backup files we keep. '''
        oldestBackupFile = self.oldestBackupFile(taskFile, glob)
        if oldestBackupFile:
            dt = oldestBackupFile.split('.')[-3]
            parts = (int(part) for part in (dt[0:4], dt[4:6], dt[6:8], dt[9:11], dt[11:13], dt[13:14]))
            oldestDateTime = date.DateTime(*parts)
            now = date.DateTime.now()
            delta = now-oldestDateTime
            return max(3, int(math.log(max(1, delta.hours() * 60))))
        else:
            return 3
    
    def oldestBackupFile(self, taskFile, glob):
        backupFiles = self.backupFiles(taskFile, glob)
        backupFiles.sort()
        return backupFiles[0] if backupFiles else None

    @staticmethod
    def backupFiles(taskFile, glob=glob.glob):
        root, ext = os.path.splitext(taskFile.filename())
        datePattern = '[0-9]'*8
        timePattern = '[0-9]'*6
        return glob('%s.%s-%s.tsk.bak'%(root, datePattern, timePattern))

    @staticmethod
    def backupFilename(taskFile, now=date.DateTime.now):
        ''' Generate a backup filename by adding '.bak' to the end and by 
            inserting a date-time string in the filename. '''
        now = now().strftime('%Y%m%d-%H%M%S')
        root, ext = os.path.splitext(taskFile.filename())
        if ext == '.bak':
            root, ext = os.path.splitext(root)
        return root + '.' + now + ext + '.bak'
                
