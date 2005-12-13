import widgets, wx, meta
from i18n import _

class SettingsPage(widgets.BookPage):
    def __init__(self, settings=None, *args, **kwargs):
        super(SettingsPage, self).__init__(*args, **kwargs)
        self.settings = settings
        self._booleanSettings = []
        self._choiceSettings = []
        self._integerSettings = []
        self._colorSettings = []
        
    def addBooleanSetting(self, section, setting, text, helpText=''):
        checkBox = wx.CheckBox(self, -1)
        checkBox.SetValue(self.settings.getboolean(section, setting))
        self.addEntry(text, checkBox, helpText)
        self._booleanSettings.append((section, setting, checkBox))

    def addChoiceSetting(self, section, setting, text, choices, helpText=''):
        choice = wx.Choice(self, -1)
        for choiceValue, choiceText in choices:
            choice.Append(choiceText, choiceValue)
            if choiceValue == self.settings.get(section, setting):
                choice.SetSelection(choice.GetCount()-1)
        if choice.GetSelection() == wx.NOT_FOUND: # force a selection if necessary
            choice.SetSelection(0)
        self.addEntry(text, choice, helpText)
        self._choiceSettings.append((section, setting, choice))
        
    def addIntegerSetting(self, section, setting, text, minimum=0, maximum=100, helpText=''):
        spin = wx.SpinCtrl(self, -1, min=minimum, max=maximum, 
            value=str(self.settings.getint(section, setting)))
        self.addEntry(text, spin, helpText)
        self._integerSettings.append((section, setting, spin))

    def addColorSetting(self, section, setting, text):
        colorButton = widgets.ColorSelect(self, -1, text, eval(self.settings.get(section, setting)))
        self.addEntry(None, colorButton)
        self._colorSettings.append((section, setting, colorButton))
                
    def ok(self):
        for section, setting, checkBox in self._booleanSettings:
            self.settings.set(section, setting, str(checkBox.IsChecked()))
        for section, setting, choice in self._choiceSettings:
            self.settings.set(section, setting, choice.GetClientData(choice.GetSelection()))
        for section, setting, spin in self._integerSettings:
            self.settings.set(section, setting, str(spin.GetValue()))
        for section, setting, colorButton in self._colorSettings:
            self.settings.set(section, setting, str(colorButton.GetColour()))
            

class SavePage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(SavePage, self).__init__(*args, **kwargs)
        self.addBooleanSetting('file', 'autosave', 
            _('Auto save after every change'))
        self.addBooleanSetting('file', 'backup', 
            _('Create backup copy before overwriting a %s file')%meta.name)
        self.addIntegerSetting('file', 'maxrecentfiles',
            _('Maximum number of recent files to remember'), minimum=0, maximum=9)
            
               
class WindowPage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(WindowPage, self).__init__(*args, **kwargs)
        self.addBooleanSetting('window', 'splash', _('Show splash screen on startup'),
            _('This setting will take effect after you restart %s')%meta.name)
        self.addBooleanSetting('window', 'hidewheniconized', 
            _('Hide main window when iconized'))
        self.addBooleanSetting('window', 'hidewhenclosed', 
            _('Minimize main window when closed'))


class LanguagePage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(LanguagePage, self).__init__(*args, **kwargs)
        self.addChoiceSetting('view', 'language', _('Language'), 
            [('en_US', _('English (US)')), 
             ('en_GB', _('English (UK)')),
             ('de_DE', _('German')),
             ('nl_NL', _('Dutch')),
             ('fr_FR', _('French')),
             ('zh_CN', _('Simplified Chinese')),
             ('ru_RU', _('Russian')),
             ('es_ES', _('Spanish')),
             ('hu_HU', _('Hungarian'))],
             _('This setting will take effect after you restart %s')%meta.name)


class ColorsPage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(ColorsPage, self).__init__(*args, **kwargs)
        for setting, label in \
            [('activetasks', _('Click this button to change the color of active tasks')), 
             ('inactivetasks', _('Click this button to change the color of inactive tasks')),
             ('completedtasks', _('Click this button to change the color of completed tasks')),
             ('overduetasks', _('Click this button to change the color of over due tasks')),
             ('duetodaytasks', _('Click this button to change the color of tasks due today'))]:
            self.addColorSetting('color', setting, label)

        
class Preferences(widgets.ListbookDialog):
    def __init__(self, settings=None, *args, **kwargs):
        self.settings = settings
        super(Preferences, self).__init__(bitmap='configure', *args, **kwargs) 
                   
    def addPages(self):
        self.SetMinSize((300, 300))
        self._interior.AddPage(WindowPage(parent=self._interior, columns=3, settings=self.settings), _('Window behavior'), bitmap='windows')
        self._interior.AddPage(SavePage(parent=self._interior, columns=3, settings=self.settings), _('Files'), bitmap='save')
        self._interior.AddPage(LanguagePage(parent=self._interior, columns=3, settings=self.settings), _('Language'), bitmap='language')
        self._interior.AddPage(ColorsPage(parent=self._interior, columns=1, settings=self.settings, growableColumn=-1), _('Colors'), bitmap='colorize')
