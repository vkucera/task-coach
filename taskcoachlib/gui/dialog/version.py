from wx.lib import hyperlink
from i18n import _
import wx, meta
from widgets import sized_controls

class VersionDialog(sized_controls.SizedDialog):
    def __init__(self, *args, **kwargs):
        version = kwargs.pop('version')
        kwargs['title'] = kwargs.get('title', 
            _('New version of %(name)s available')%dict(name=meta.data.name))
        super(VersionDialog, self).__init__(*args, **kwargs)
        pane = self.GetContentsPane()
        pane.SetSizerType("vertical")
        panel = sized_controls.SizedPanel(pane)
        panel.SetSizerType('horizontal')
        messageInfo = dict(version=version, name=meta.data.name)
        message = _('Version %(version)s of %(name)s is available from')%messageInfo
        wx.StaticText(panel, label=message)
        hyperlink.HyperLinkCtrl(panel, label=meta.data.url)
        self.check = wx.CheckBox(pane, label=_('Notify me of new versions.'))
        self.check.SetValue(True)
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK))
        self.Fit()
