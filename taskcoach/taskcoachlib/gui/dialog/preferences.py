# -*- coding: UTF-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2008 Jerome Laheurte <fraca7@free.fr>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>

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

import wx
from taskcoachlib import meta, widgets
from taskcoachlib.i18n import _


class SettingsPage(widgets.BookPage):
    def __init__(self, settings=None, *args, **kwargs):
        super(SettingsPage, self).__init__(*args, **kwargs)
        self.settings = settings
        self._booleanSettings = []
        self._choiceSettings = []
        self._integerSettings = []
        self._colorSettings = []
        self._pathSettings = []
        self._textSettings = []
        
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

    def addPathSetting(self, section, setting, text, helpText=''):
        pathChooser = widgets.DirectoryChooser(self, wx.ID_ANY)
        pathChooser.SetPath(self.settings.get(section, setting))
        self.addEntry(text, pathChooser, helpText)
        self._pathSettings.append((section, setting, pathChooser))

    def addTextSetting(self, section, setting, text, helpText=''):
        textChooser = wx.TextCtrl(self, wx.ID_ANY, self.settings.get(section, setting))
        self.addEntry(text, textChooser, helpText)
        self._textSettings.append((section, setting, textChooser))

    def addText(self, label, text):
        self.addEntry(label, text)
                
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
        for section, setting, btn in self._pathSettings:
            self.settings.set(section, setting, btn.GetPath())
        for section, setting, txt in self._textSettings:
            self.settings.set(section, setting, txt.GetValue())

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
        self.addPathSetting('file', 'attachmentbase', _('Attachement base directory'),
                            _('When adding an attachment, try to make its path\nrelative to this one.'))
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
              _('When the main window was iconized last session'))])
        self.addBooleanSetting('version', 'notify',
            _('Check for new version of %(name)s on startup')%meta.data.metaDict)
        self.addBooleanSetting('window', 'hidewheniconized', 
            _('Hide main window when iconized'))
        self.addBooleanSetting('window', 'hidewhenclosed', 
            _('Minimize main window when closed'))
        self.addBooleanSetting('window', 'blinktaskbariconwhentrackingeffort',
            _('Make clock in the task bar tick when tracking effort'))
        self.addBooleanSetting('view', 'descriptionpopups',
            _('Show a popup with the description of an item when hovering over it'))
        self.fit()


class LanguagePage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(LanguagePage, self).__init__(*args, **kwargs)
        self.addChoiceSetting('view', 'language', _('Language'), 
            [('pt_BR', u'Português brasileiro (Brazilian Portuguese)'),
             ('br_FR', 'Brezhoneg (Breton)'),
             ('bg_BG', u'български (Bulgarian)'),
             ('zh_CN', u'简体中文 (Simplified Chinese)'),
             ('zh_TW', u'正體字 (Traditional Chinese)'),
             ('cs_CS', u'Čeština (Czech)'),
             ('da_DA', 'Dansk (Danish)'),
             ('nl_NL', 'Nederlands (Dutch)'),
             ('en_GB', 'English (UK)'),
             ('en_US', 'English (US)'), 
             ('fi_FI', 'Suomi (Finnish)'),
             ('fr_FR', u'Français (French)'),
             ('gl_ES', 'Galego (Galician)'),
             ('de_DE', 'Deutsch (German)'),
             ('el_GR', u'ελληνικά (Greek)'),
             ('he_IL', u'עברית (Hebrew)'),
             ('hu_HU', 'Magyar (Hungarian)'),
             ('it_IT', 'Italiano (Italian)'),
             ('ja_JP', u'日本語 (Japanese)'),
             ('ko_KO', u'한국어/조선말 (Korean)'),
             ('lv_LV', u'Latviešu (Latvian)'),
             ('nb_NO', u'Bokmål (Norwegian Bokmal)'),
             ('fa_IR', u'فارسی (Persian)'),
             ('pl_PL', u'Język polski (Polish)'),
             ('pt_PT', u'Português (Portuguese)'),
             ('ro_RO', u'Română (Romanian)'),
             ('ru_RU', u'Русский (Russian)'),
             ('sk_SK', u'Slovenčina (Slovak)'),
             ('es_ES', u'Español (Spanish)'),
             ('sv_SE', 'Svenska (Swedish)'),
             ('th_TH', u'ภาษาไทย (Thai)'),
             ('tr_TR', u'Türkçe (Turkish)'),
             ('uk_UA', u'украї́нська мо́ва (Ukranian)')],
             _('This setting will take effect after you restart %s')%meta.name)
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(panel, 
            label=_('''If your language is not available, or the translation needs 
improving, please consider helping. See:'''))
        sizer.Add(text)
        url = meta.url + 'i18n.html'
        urlCtrl = wx.HyperlinkCtrl(panel, -1, label=url, url=url)
        sizer.Add(urlCtrl)
        panel.SetSizerAndFit(sizer)
        self.addText(_('Language not found?'), panel)
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


class FeaturesPage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(FeaturesPage, self).__init__(*args, **kwargs)
        self.addBooleanSetting('feature', 'notes', _('Allow for taking notes'), 
            _('This setting will take effect after you restart %s')%meta.name)
        self.addIntegerSetting('view', 'efforthourstart',
            _('Hour of start of work day'), minimum=0, maximum=23)
        self.addIntegerSetting('view', 'efforthourend',
            _('Hour of end of work day'), minimum=1, maximum=24)
        self.addChoiceSetting('view', 'effortminuteinterval',
            _('Minutes between task start/end times'),
            [('5', '5'), ('10', '10'), ('15', '15'), ('20', '20'), ('30', '30')])
        self.fit()
        

class TaskBehaviorPage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(TaskBehaviorPage, self).__init__(*args, **kwargs)
        self.addBooleanSetting('behavior', 'markparentcompletedwhenallchildrencompleted',
            _('Mark parent task completed when all children are completed'))
        self.fit()
        
        
class EditorPage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(EditorPage, self).__init__(*args, **kwargs)
        self.addBooleanSetting('editor', 'maccheckspelling',
            _('Check spelling in editors'))
        self.fit()
        
    def ok(self):
        super(EditorPage, self).ok()
        widgets.MultiLineTextCtrl.CheckSpelling = \
            self.settings.getboolean('editor', 'maccheckspelling')


class SyncMLPage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(SyncMLPage, self).__init__(*args, **kwargs)

        self.addBooleanSetting('syncml', 'synctasks', _('Enable tasks synchronization'))
##         self.addBooleanSetting('syncml', 'syncnotes', _('Enable notes synchronization'))
##         self.addBooleanSetting('syncml', 'syncefforts', _('Enable efforts synchronization'))

        self.addTextSetting('syncml', 'url', _('SyncML server URL'))
        self.addTextSetting('syncml', 'username', _('User name/ID'))
        self.addTextSetting('syncml', 'taskdbname', _('Tasks database name'))
##         self.addTextSetting('syncml', 'notedbname', _('Notes database name'))
##         self.addTextSetting('syncml', 'effortdbname', _('Efforts database name'))

        self.fit()

class Preferences(widgets.ListbookDialog):
    def __init__(self, settings=None, *args, **kwargs):
        self.settings = settings
        super(Preferences, self).__init__(bitmap='configure', *args, **kwargs) 
                   
    def addPages(self):
        self.SetMinSize((300, 430))
        pages = [\
            (WindowBehaviorPage(parent=self._interior, columns=3, settings=self.settings), _('Window behavior'), 'windows'),
            (TaskBehaviorPage(parent=self._interior, columns=2, settings=self.settings), _('Task behavior'), 'behavior'),
            (SavePage(parent=self._interior, columns=3, settings=self.settings), _('Files'), 'save'),
            (LanguagePage(parent=self._interior, columns=3, settings=self.settings), _('Language'), 'language'),
            (ColorsPage(parent=self._interior, columns=1, settings=self.settings, growableColumn=-1), _('Colors'), 'colorize'),
            (FeaturesPage(parent=self._interior, columns=3, settings=self.settings), _('Features'), 'behavior'),
            (SyncMLPage(parent=self._interior, columns=3, settings=self.settings), _('SyncML'), 'sync')]
        if '__WXMAC__' in wx.PlatformInfo:
            pages.append((EditorPage(parent=self._interior, columns=2, settings=self.settings), _('Editor'), 'edit'))
        for page, title, bitmap in pages:
            self._interior.AddPage(page, title, bitmap=bitmap)
