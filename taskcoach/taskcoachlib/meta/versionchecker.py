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

import threading, wx, urllib2
import data


# We don't use cElementTree because py2exe somehow does not
# include cElementTree. ElementTree is no problem though...
# We also can't use cElementTree (easily) because it's not part of the
# Python 2.4 module library, so if import of ElementTree fails we get our
# own copy from the thirdparty package.
try:
    import xml.etree.ElementTree as ElementTree
except ImportError:
    from taskcoachlib.thirdparty import ElementTree
   
   
class VersionChecker(threading.Thread):
    def __init__(self, settings):
        self.settings = settings
        super(VersionChecker, self).__init__()
        
    def _set_daemon(self):
        return True # Don't block application exit
        
    def run(self):
        latestVersion = self.getLatestVersion()
        lastVersionNotified = self.settings.get('version', 'notified')
        if latestVersion > lastVersionNotified and latestVersion > data.version:
            self.settings.set('version', 'notified', latestVersion)
            self.notifyUser(latestVersion)
            
    def getLatestVersion(self):
        try:
            padFile = self.retrievePadFile()
        except urllib2.URLError:
            return self.settings.get('version', 'notified')
        try:
            pad = ElementTree.parse(padFile)
        except ElementTree.ExpatError:
            # This can happen e.g. when connected to a hotel network that
            # returns the same webpage for each url requested
            return self.settings.get('version', 'notified')
        return pad.findtext('Program_Info/Program_Version')
    
    def retrievePadFile(self):
        return urllib2.urlopen(data.pad)
    
    def notifyUser(self, latestVersion):
        # Must use CallAfter because this is a non-GUI thread
        wx.CallAfter(self.showDialog, latestVersion)
        
    def showDialog(self, version):
        from taskcoachlib import gui # import here to prevent circular import
        dialog = gui.dialog.version.VersionDialog(wx.GetApp().GetTopWindow(), 
                                                  version=version)   
        dialog.ShowModal()
        self.settings.set('version', 'notify', str(dialog.check.GetValue()))     
        dialog.Destroy()

