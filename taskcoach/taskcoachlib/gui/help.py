import meta
import wx.lib.dialogs

def show(text, title):
    dialog = wx.lib.dialogs.ScrolledMessageDialog(None, text, title)
    dialog.ShowModal()

def Colors():
    show(meta.colorsText, "Help: Colors")

def Tasks():
    show(meta.tasksText, "Help: Tasks")

def About():
    show(meta.aboutText, "Help: About %s"%meta.name)

def License():
    show(meta.licenseText, "Help: %s license"%meta.name)
