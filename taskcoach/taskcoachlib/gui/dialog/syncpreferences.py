
from taskcoachlib.gui.dialog.preferences import SettingsPageBase
from taskcoachlib import widgets
from taskcoachlib.syncml.config import SyncMLConfigNode
from taskcoachlib.i18n import _

class SyncMLBasePage(SettingsPageBase):
    def __init__(self, iocontroller=None, *args, **kwargs):
        super(SyncMLBasePage, self).__init__(*args, **kwargs)

        self.iocontroller = iocontroller
        self.config = iocontroller.syncMLConfig()

    def get(self, section, name):
        if section == 'access':
            if name in [ 'syncUrl' ]:
                return str(self.config.children()[0]['spds']['syncml']['Conn'].get(name))
            elif name in [ 'username' ]:
                return str(self.config.children()[0]['spds']['syncml']['Auth'].get(name))
        elif section == 'task':
            for child in self.config.children()[0]['spds']['sources'].children():
                if child.name.endswith('Tasks'):
                    break
            else:
                return ''

            return child.get(name)
        elif section == 'note':
            for child in self.config.children()[0]['spds']['sources'].children():
                if child.name.endswith('Notes'):
                    break
            else:
                return ''

            return child.get(name)
        else:
            return ''

    def set(self, section, name, value):
        if section == 'access':
            if name in [ 'syncUrl' ]:
                self.config.children()[0]['spds']['syncml']['Conn'].set(name, value)
            elif name in [ 'username' ]:
                self.config.children()[0]['spds']['syncml']['Auth'].set(name, value)
        elif section == 'task':
            for child in self.config.children()[0]['spds']['sources'].children():
                if child.name.endswith('Tasks'):
                    break
            else:
                return

            child.set(name, value)
        elif section == 'note':
            for child in self.config.children()[0]['spds']['sources'].children():
                if child.name.endswith('Notes'):
                    break
            else:
                return

            child.set(name, value)

    def ok(self):
        super(SyncMLBasePage, self).ok()

        self.iocontroller.setSyncMLConfig(self.config)


class SyncMLAccessPage(SyncMLBasePage):
    def __init__(self, *args, **kwargs):
        super(SyncMLAccessPage, self).__init__(*args, **kwargs)

        self.addTextSetting('access', 'syncUrl', _('SyncML server URL'))
        self.addTextSetting('access', 'username', _('User name/ID'))

        self.fit()


class SyncMLTaskPage(SyncMLBasePage):
    def __init__(self, *args, **kwargs):
        super(SyncMLTaskPage, self).__init__(*args, **kwargs)

        self.addBooleanSetting('task', 'dosync', _('Enable tasks synchronization'))
        self.addTextSetting('task', 'uri', _('Tasks database name'))

        self.addChoiceSetting('task', 'preferredsyncmode', _('Preferred synchonization mode'),
                              [('TWO_WAY', _('Two way')),
                               ('SLOW', _('Slow')),
                               ('ONE_WAY_FROM_CLIENT', _('One way from client')),
                               ('REFRESH_FROM_CLIENT', _('Refresh from client')),
                               ('ONE_WAY_FROM_SERVER', _('One way from server')),
                               ('REFRESH_FROM_SERVER', _('Refresh from server'))])

        self.fit()


class SyncMLNotePage(SyncMLBasePage):
    def __init__(self, *args, **kwargs):
        super(SyncMLNotePage, self).__init__(*args, **kwargs)

        self.addBooleanSetting('note', 'dosync', _('Enable notes synchronization'))
        self.addTextSetting('note', 'uri', _('Notes database name'))

        self.addChoiceSetting('note', 'preferredsyncmode', _('Preferred synchonization mode'),
                              [('TWO_WAY', _('Two way')),
                               ('SLOW', _('Slow')),
                               ('ONE_WAY_FROM_CLIENT', _('One way from client')),
                               ('REFRESH_FROM_CLIENT', _('Refresh from client')),
                               ('ONE_WAY_FROM_SERVER', _('One way from server')),
                               ('REFRESH_FROM_SERVER', _('Refresh from server'))])

        self.fit()


class SyncMLPreferences(widgets.ListbookDialog):
    def __init__(self, iocontroller=None, *args, **kwargs):
        self.iocontroller = iocontroller

        super(SyncMLPreferences, self).__init__(bitmap='iocontrollerure', *args, **kwargs)

    def addPages(self):
        self.SetMinSize((300, 500))

        pages = [ (SyncMLAccessPage(parent=self._interior, columns=3, iocontroller=self.iocontroller,
                                    growableColumn=1),
                   _('Access'), 'windows'),
                  (SyncMLTaskPage(parent=self._interior, columns=3, iocontroller=self.iocontroller),
                   _('Tasks'), 'windows'),
                  (SyncMLNotePage(parent=self._interior, columns=3, iocontroller=self.iocontroller),
                   _('Notes'), 'windows') ]

        for page, title, bitmap in pages:
            self._interior.AddPage(page, title, bitmap=bitmap)
