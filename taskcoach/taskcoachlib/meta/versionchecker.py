import threading, wx, meta, urllib2
from i18n import _
import gui.dialog.version

# We don't use cElementTree because py2exe somehow does not
# include cElementTree. ElementTree is no problem though...
# We also can't use cElementTree (easily) because it's not part of the
# Python 2.4 module library, so if import of ElementTree fails we get our
# own copy from the thirdparty package.
try:
    import xml.etree.ElementTree as ElementTree
except ImportError:
    import thirdparty.ElementTree as ElementTree
   
   
class VersionChecker(threading.Thread):
    def __init__(self, settings):
        self.settings = settings
        super(VersionChecker, self).__init__()
        
    def run(self):
        latestVersion = self.getLatestVersion()
        lastVersionNotified = self.settings.get('version', 'notified')
        if latestVersion > lastVersionNotified:
            self.settings.set('version', 'notified', latestVersion)
            self.notifyUser(latestVersion)
            
    def getLatestVersion(self):
        try:
            padFile = self.retrievePadFile()
        except urllib2.URLError:
            return self.settings.get('version', 'notified')
        pad = ElementTree.parse(padFile)
        return pad.findtext('Program_Info/Program_Version')
    
    def retrievePadFile(self):
        return urllib2.urlopen(meta.data.pad)
    
    def notifyUser(self, latestVersion):
        # Must use CallAfter because this is a non-GUI thread
        wx.CallAfter(self.showDialog, latestVersion)
        
    def showDialog(self, version):
        dialog = gui.dialog.version.VersionDialog(wx.GetApp().GetTopWindow(), 
                                                  version=version)   
        dialog.ShowModal()
        self.settings.set('version', 'notify', str(dialog.check.GetValue()))     
        dialog.Destroy()