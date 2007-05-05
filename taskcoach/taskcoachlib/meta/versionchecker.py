import threading, wx, meta, urllib2
from i18n import _
import gui.dialog.version

    
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
        import xml.etree.cElementTree
        try:
            padFile = self.retrievePadFile()
        except urllib2.URLError:
            return self.settings.get('version', 'notified')
        pad = xml.etree.cElementTree.parse(padFile)
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