import meta, help
import wx.lib.dialogs
from i18n import _

class HelpDialog(wx.lib.dialogs.ScrolledMessageDialog):
    pass
     
def show(text, title):
    dialog = HelpDialog(None, text, title)
    dialog.Show()
    return dialog

def Colors():
    return show(help.colorsText, _('Help: Colors'))

def Tasks():
    return show(help.tasksText, _('Help: Tasks'))

def About():
    return show(help.aboutText, _('Help: About %s')%meta.name)

def License():
    return show(meta.licenseText, _('Help: %s license')%meta.name)
