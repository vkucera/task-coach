# -*- coding: UTF-8 -*-

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
        
    def addIntegerSetting(self, section, setting, text, minimum=0, maximum=100,
            helpText=''):
        spin = wx.SpinCtrl(self, min=minimum, max=maximum, size=(40, -1),
            value=str(self.settings.getint(section, setting)))
        self.addEntry(text, spin, helpText)
        self._integerSettings.append((section, setting, spin))

    def addColorSetting(self, section, setting, text):
        colorButton = widgets.ColorSelect(self, -1, text,
            eval(self.settings.get(section, setting)))
        self.addEntry(None, colorButton)
        self._colorSettings.append((section, setting, colorButton))
                
    def ok(self):
        for section, setting, checkBox in self._booleanSettings:
            self.settings.set(section, setting, str(checkBox.IsChecked()))
        for section, setting, choice in self._choiceSettings:
            self.settings.set(section, setting, 
                              choice.GetClientData(choice.GetSelection()))
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
        self.addBooleanSetting('file', 'saveinifileinprogramdir',
            _('Save settings (%s.ini) in same directory as the program') \
              %meta.filename, 
            _('(For running %s from a removable medium)')%meta.name)
        self.fit()
            
               
class WindowBehaviorPage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(WindowBehaviorPage, self).__init__(*args, **kwargs)
        self.addBooleanSetting('window', 'splash', 
            _('Show splash screen on startup'))
        self.addBooleanSetting('window', 'tips', 
            _('Show tips window on startup'))
        self.addChoiceSetting('window', 'starticonized',
            _('Start with the main window iconized'),
            [('Never', _('Never')), ('Always', _('Always')), 
             ('WhenClosedIconized', 
              _('When the main windows was iconized last session'))])
        self.addBooleanSetting('version', 'notify',
            _('Check for new version of %(name)s on startup')%meta.data.metaDict)
        self.addBooleanSetting('window', 'hidewheniconized', 
            _('Hide main window when iconized'))
        self.addBooleanSetting('window', 'hidewhenclosed', 
            _('Minimize main window when closed'))
        self.addBooleanSetting('window', 'blinktaskbariconwhentrackingeffort',
            _('Make clock in the task bar tick when tracking effort'))
        self.fit()


class LanguagePage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(LanguagePage, self).__init__(*args, **kwargs)
        self.addChoiceSetting('view', 'language', _('Language'), 
            [('en_US', 'English (US)'), 
             ('en_GB', 'English (UK)'),
             ('de_DE', 'Deutsch (German)'),
             ('nl_NL', 'Nederlands (Dutch)'),
             ('fr_FR', u'Français (French)'),
             ('zh_CN', u'简体中文 (Simplified Chinese)'),
             ('ja_JP', u'日本語 (Japanese)'),
             ('ru_RU', u'Русский (Russian)'),
             ('es_ES', u'Español (Spanish)'),
             ('sk_SK', u'Slovenčina (Slovak)'),
             ('hu_HU', 'Magyar (Hungarian)'),
             ('br_FR', 'Brezhoneg (Breton)')],
             _('This setting will take effect after you restart %s')%meta.name)
        self.fit()


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
        self.fit()


class TaskBehaviorPage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(TaskBehaviorPage, self).__init__(*args, **kwargs)
        self.addBooleanSetting('behavior', 'markparentcompletedwhenallchildrencompleted',
            _('Mark parent task completed when all children are completed'))
        self.fit()
        
        
class Preferences(widgets.ListbookDialog):
    def __init__(self, settings=None, *args, **kwargs):
        self.settings = settings
        super(Preferences, self).__init__(bitmap='configure', *args, **kwargs) 
                   
    def addPages(self):
        self.SetMinSize((300, 300))
        for page, title, bitmap in [\
            (WindowBehaviorPage(parent=self._interior, columns=3, settings=self.settings), _('Window behavior'), 'windows'),
            (TaskBehaviorPage(parent=self._interior, columns=2, settings=self.settings), _('Task behavior'), 'behavior'),
            (SavePage(parent=self._interior, columns=3, settings=self.settings), _('Files'), 'save'),
            (LanguagePage(parent=self._interior, columns=3, settings=self.settings), _('Language'), 'language'),
            (ColorsPage(parent=self._interior, columns=1, settings=self.settings, growableColumn=-1), _('Colors'), 'colorize')]:
            self._interior.AddPage(page, title, bitmap=bitmap)
