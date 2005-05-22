import meta, help
import wx.lib.dialogs
from i18n import _

def show(text, title):
    dialog = wx.lib.dialogs.ScrolledMessageDialog(None, text, title)
    dialog.ShowModal()

def Colors():
    show(help.colorsText, _('Help: Colors'))

def Tasks():
    show(help.tasksText, _('Help: Tasks'))

def About():
    show(help.aboutText, _('Help: About %s')%meta.name)

def License():
    show(meta.licenseText, _('Help: %s license')%meta.name)
