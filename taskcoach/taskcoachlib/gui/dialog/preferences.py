# -*- coding: UTF-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>
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
from taskcoachlib import meta, widgets, notify
from taskcoachlib.gui import artprovider
from taskcoachlib.domain import date
from taskcoachlib.i18n import _


class FontColorSyncer(object):
    def __init__(self, fgColorButton, bgColorButton, fontButton):
        self._fgColorButton = fgColorButton
        self._bgColorButton = bgColorButton
        self._fontButton = fontButton
        fgColorButton.Bind(wx.EVT_COLOURPICKER_CHANGED, self.onFgColorPicked)
        bgColorButton.Bind(wx.EVT_COLOURPICKER_CHANGED, self.onBgColorPicked)
        fontButton.Bind(wx.EVT_FONTPICKER_CHANGED, self.onFontPicked)

    def onFgColorPicked(self, event): # pylint: disable-msg=W0613
        self._fontButton.SetColour(self._fgColorButton.GetColour())
        
    def onBgColorPicked(self, event): # pylint: disable-msg=W0613
        self._fontButton.SetBackgroundColour(self._bgColorButton.GetColour())

    def onFontPicked(self, event): # pylint: disable-msg=W0613
        fontColor = self._fontButton.GetSelectedColour() 
        if  fontColor != self._fgColorButton.GetColour() and fontColor != wx.BLACK:
            self._fgColorButton.SetColour(self._fontButton.GetSelectedColour())
        else:
            self._fontButton.SetColour(self._fgColorButton.GetColour())


class SettingsPageBase(widgets.BookPage):
    def __init__(self, *args, **kwargs):
        super(SettingsPageBase, self).__init__(*args, **kwargs)
        self._booleanSettings = []
        self._choiceSettings = []
        self._multipleChoiceSettings = []
        self._integerSettings = []
        self._colorSettings = []
        self._fontSettings = []
        self._iconSettings = []
        self._pathSettings = []
        self._textSettings = []
        self._syncers = []
        
    def addBooleanSetting(self, section, setting, text, helpText=''):
        checkBox = wx.CheckBox(self, -1)
        checkBox.SetValue(self.getboolean(section, setting))
        self.addEntry(text, checkBox, helpText=helpText)
        self._booleanSettings.append((section, setting, checkBox))
        return checkBox

    def addChoiceSetting(self, section, setting, text, helpText, *listsOfChoices, **kwargs):
        choiceCtrls = []
        currentValue = self.get(section, setting)
        for choices, currentValuePart in zip(listsOfChoices, currentValue.split('_')):
            choiceCtrl = wx.Choice(self, -1)
            choiceCtrls.append(choiceCtrl)
            for choiceValue, choiceText in choices:
                choiceCtrl.Append(choiceText, choiceValue)
                if choiceValue == currentValuePart:
                    choiceCtrl.SetSelection(choiceCtrl.GetCount()-1)
            if choiceCtrl.GetSelection() == wx.NOT_FOUND: # force a selection if necessary
                choiceCtrl.SetSelection(0)
        # pylint: disable-msg=W0142
        self.addEntry(text, *choiceCtrls, helpText=helpText, 
                      flags=kwargs.get('flags', None)) 
        self._choiceSettings.append((section, setting, choiceCtrls))
        return choiceCtrls

    def enableChoiceSetting(self, section, setting, enabled):
        for theSection, theSetting, ctrls in self._choiceSettings:
            if theSection == section and theSetting == setting:
                for ctrl in ctrls:
                    ctrl.Enable(enabled)
                break

    def addMultipleChoiceSettings(self, section, setting, text, choices, helpText='', **kwargs):
        ''' choices is a list of (number, text) tuples. '''
        multipleChoice = wx.CheckListBox(self, choices=[choice[1] for choice in choices])
        checkedNumbers = eval(self.get(section, setting))
        for index, choice in enumerate(choices):
            multipleChoice.Check(index, choice[0] in checkedNumbers)
        self.addEntry(text, multipleChoice, helpText=helpText, growable=True, 
                      flags=kwargs.get('flags', None))
        self._multipleChoiceSettings.append((section, setting, multipleChoice, 
                                             [choice[0] for choice in choices]))
        
    def addIntegerSetting(self, section, setting, text, minimum=0, maximum=100,
            helpText='', flags=None):
        intValue = self.getint(section, setting)
        spin = widgets.SpinCtrl(self, min=minimum, max=maximum, size=(65, -1),
            value=intValue)
        self.addEntry(text, spin, helpText=helpText, flags=flags)
        self._integerSettings.append((section, setting, spin))

    def addAppearanceHeader(self):
        self.addEntry('', _('Foreground color'), _('Background color'),
                      _('Font'), _('Icon'), flags=[wx.ALL|wx.ALIGN_CENTER]*5)

    def addAppearanceSetting(self, fgColorSection, fgColorSetting, bgColorSection,
                             bgColorSetting, fontSection, fontSetting, iconSection,
                             iconSetting, text):
        currentFgColor = eval(self.get(fgColorSection, fgColorSetting))
        fgColorButton = wx.ColourPickerCtrl(self, col=currentFgColor)
        currentBgColor = eval(self.get(bgColorSection, bgColorSetting))
        bgColorButton = wx.ColourPickerCtrl(self, col=currentBgColor)
        defaultFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        nativeInfoString = self.get(fontSection, fontSetting)
        currentFont = wx.FontFromNativeInfoString(nativeInfoString) if nativeInfoString else None
        fontButton = widgets.FontPickerCtrl(self, font=currentFont or defaultFont, colour=currentFgColor)
        fontButton.SetBackgroundColour(currentBgColor)        
        iconEntry = wx.combo.BitmapComboBox(self, style=wx.CB_READONLY)
        imageNames = sorted(artprovider.chooseableItemImages.keys())
        for imageName in imageNames:
            label = artprovider.chooseableItemImages[imageName]
            bitmap = wx.ArtProvider_GetBitmap(imageName, wx.ART_MENU, (16, 16))
            item = iconEntry.Append(label, bitmap)
            iconEntry.SetClientData(item, imageName)
        currentIcon = self.get(iconSection, iconSetting)
        currentSelectionIndex = imageNames.index(currentIcon)
        iconEntry.SetSelection(currentSelectionIndex) # pylint: disable-msg=E1101

        self.addEntry(text, fgColorButton, bgColorButton, fontButton, iconEntry, 
                      flags=(wx.ALL|wx.ALIGN_CENTER_VERTICAL, 
                             wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL,
                             wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 
                             wx.ALL|wx.ALIGN_CENTER_VERTICAL, # wx.EXPAND causes the button to be top aligned on Mac OS X
                             wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL))
        self._colorSettings.append((fgColorSection, fgColorSetting, fgColorButton))
        self._colorSettings.append((bgColorSection, bgColorSetting, bgColorButton))
        self._iconSettings.append((iconSection, iconSetting, iconEntry))        
        self._fontSettings.append((fontSection, fontSetting, fontButton))
        self._syncers.append(FontColorSyncer(fgColorButton, bgColorButton, fontButton))
        
    def addPathSetting(self, section, setting, text, helpText=''):
        pathChooser = widgets.DirectoryChooser(self, wx.ID_ANY)
        pathChooser.SetPath(self.get(section, setting))
        self.addEntry(text, pathChooser, helpText=helpText)
        self._pathSettings.append((section, setting, pathChooser))

    def addTextSetting(self, section, setting, text, helpText=''):
        textChooser = wx.TextCtrl(self, wx.ID_ANY, self.get(section, setting))
        self.addEntry(text, textChooser, helpText=helpText)
        self._textSettings.append((section, setting, textChooser))

    def setTextSetting(self, section, setting, value):
        for theSection, theSetting, textChooser in self._textSettings:
            if theSection == section and theSetting == setting:
                textChooser.SetValue(value)

    def enableTextSetting(self, section, setting, enabled):
        for theSection, theSetting, textChooser in self._textSettings:
            if theSection == section and theSetting == setting:
                textChooser.Enable(enabled)
                break

    def addText(self, label, text):
        self.addEntry(label, text)

    def ok(self):
        for section, setting, checkBox in self._booleanSettings:
            self.set(section, setting, str(checkBox.IsChecked()))
        for section, setting, choiceCtrls in self._choiceSettings:
            value = '_'.join([choice.GetClientData(choice.GetSelection()) for choice in choiceCtrls])
            self.set(section, setting, value)
        for section, setting, multipleChoice, choices in self._multipleChoiceSettings:
            self.set(section, setting,
                     str([choices[index] for index in range(len(choices)) if multipleChoice.IsChecked(index)]))
        for section, setting, spin in self._integerSettings:
            self.set(section, setting, str(spin.GetValue()))
        for section, setting, colorButton in self._colorSettings:
            self.set(section, setting, str(colorButton.GetColour()))
        for section, setting, fontButton in self._fontSettings:
            nativeFontInfoDesc = fontButton.GetSelectedFont().GetNativeFontInfoDesc()
            defaultFontInfoDesc = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT).GetNativeFontInfoDesc()
            if nativeFontInfoDesc != defaultFontInfoDesc:
                self.set(section, setting, nativeFontInfoDesc)
        for section, setting, iconEntry in self._iconSettings:
            iconName = iconEntry.GetClientData(iconEntry.GetSelection())
            self.set(section, setting, iconName)
        for section, setting, btn in self._pathSettings:
            self.set(section, setting, btn.GetPath())
        for section, setting, txt in self._textSettings:
            self.set(section, setting, txt.GetValue())

    def get(self, section, name):
        raise NotImplementedError

    def getint(self, section, name):
        return int(self.get(section, name))

    def getboolean(self, section, name):
        return self.get(section, name) == 'True'

    def set(self, section, name, value):
        raise NotImplementedError


class SettingsPage(SettingsPageBase):
    def __init__(self, settings=None, *args, **kwargs):
        self.settings = settings
        super(SettingsPage, self).__init__(*args, **kwargs)
        
    def addEntry(self, text, *controls, **kwargs): # pylint: disable-msg=W0221
        helpText = kwargs.pop('helpText', '')
        if helpText == 'restart':
            helpText = _('This setting will take effect\nafter you restart %s')%meta.name
        if helpText:
            controls = controls + (helpText,)
        super(SettingsPage, self).addEntry(text, *controls, **kwargs)

    def get(self, section, name):
        return self.settings.get(section, name)

    def getint(self, section, name):
        return self.settings.getint(section, name)

    def getboolean(self, section, name):
        return self.settings.getboolean(section, name)

    def set(self, section, name, value):
        if section is not None:
            self.settings.set(section, name, value)


class SavePage(SettingsPage):
    pageName = 'save'
    pageTitle = _('Files')
    pageIcon = 'save'
    
    def __init__(self, *args, **kwargs):
        super(SavePage, self).__init__(columns=3, *args, **kwargs)
        self.addBooleanSetting('file', 'autosave', 
            _('Auto save after every change'))
        self.addBooleanSetting('file', 'backup', 
            _('Create a backup copy before\noverwriting a %s file')%meta.name)
        self.addBooleanSetting('file', 'saveinifileinprogramdir',
            _('Save settings (%s.ini) in the same\ndirectory as the program') \
              %meta.filename, 
            _('For running %s from a removable medium')%meta.name)
        self.addPathSetting('file', 'attachmentbase', _('Attachment base directory'),
                            _('When adding an attachment, try to make\nits path relative to this one.'))
        self.addMultipleChoiceSettings('file', 'autoimport', 
                                       _('Before saving, automatically import from'), 
                                       [('Todo.txt', _('Todo.txt format'))],
                                       helpText=_('Before saving, %s automatically imports tasks\n'
                                                  'from a Todo.txt file with the same name as the task file,\n'
                                                  'but with extension .txt')%meta.name)
        self.addMultipleChoiceSettings('file', 'autoexport', 
                                       _('When saving, automatically export to'), 
                                       [('Todo.txt', _('Todo.txt format'))],
                                       helpText=_('When saving, %s automatically exports tasks\n'
                                                  'to a Todo.txt file with the same name as the task file,\n'
                                                  'but with extension .txt')%meta.name)
        self.fit()
            
               
class WindowBehaviorPage(SettingsPage):
    pageName = 'window'
    pageTitle = _('Window behavior')
    pageIcon = 'windows'
    
    def __init__(self, *args, **kwargs):
        super(WindowBehaviorPage, self).__init__(columns=2, growableColumn=-1, *args, **kwargs)
        self.addBooleanSetting('window', 'splash', 
            _('Show splash screen on startup'))
        self.addBooleanSetting('window', 'tips', 
            _('Show tips window on startup'))
        self.addChoiceSetting('window', 'starticonized',
            _('Start with the main window iconized'), '',
            [('Never', _('Never')), ('Always', _('Always')), 
             ('WhenClosedIconized', 
              _('If it was iconized last session'))])
        self.addBooleanSetting('version', 'notify',
            _('Check for new version of %(name)s on startup')%meta.data.metaDict)
        self.addBooleanSetting('window', 'hidewheniconized', 
            _('Hide main window when iconized'))
        self.addBooleanSetting('window', 'hidewhenclosed', 
            _('Minimize main window when closed'))
        self.addBooleanSetting('window', 'blinktaskbariconwhentrackingeffort',
            _('Make clock in the task bar tick when tracking effort'))
        self.addBooleanSetting('view', 'descriptionpopups',
            _('Show a popup with the description of an item\nwhen hovering over it'))
        self.fit()


class LanguagePage(SettingsPage):
    pageName = 'language'
    pageTitle = _('Language')
    pageIcon = 'person_talking_icon'
    
    def __init__(self, *args, **kwargs):
        super(LanguagePage, self).__init__(columns=3, *args, **kwargs) 
        choices = \
            [('', _('Let the system determine the language')),
             ('ar', u'الْعَرَبيّة (Arabic)'),
             ('eu_ES', 'Euskal Herria (Basque)'),
             ('bs_BA', u'босански (Bosnian)'),
             ('pt_BR', u'Português brasileiro (Brazilian Portuguese)'),
             ('br_FR', 'Brezhoneg (Breton)'),
             ('bg_BG', u'български (Bulgarian)'),
             ('ca_ES', u'Català (Catalan)'),
             ('zh_CN', u'简体中文 (Simplified Chinese)'),
             ('zh_TW', u'正體字 (Traditional Chinese)'),
             ('cs_CS', u'Čeština (Czech)'),
             ('da_DA', 'Dansk (Danish)'),
             ('nl_NL', 'Nederlands (Dutch)'),
             ('en_AU', 'English (Australia)'),
             ('en_CA', 'English (Canada)'), 
             ('en_GB', 'English (UK)'),
             ('en_US', 'English (US)'), 
             ('eo', 'Esperanto'),
             ('et_EE', 'Eesti keel (Estonian)'),
             ('fi_FI', 'Suomi (Finnish)'),
             ('fr_FR', u'Français (French)'),
             ('gl_ES', 'Galego (Galician)'),
             ('de_DE', 'Deutsch (German)'),
             ('nds_DE', 'Niederdeutsche Sprache (Low German)'),
             ('el_GR', u'ελληνικά (Greek)'),
             ('he_IL', u'עברית (Hebrew)'),
             ('hi_IN', u'हिन्दी, हिंदी (Hindi)'),
             ('hu_HU', 'Magyar (Hungarian)'),
             ('id_ID', 'Bahasa Indonesia (Indonesian)'),
             ('it_IT', 'Italiano (Italian)'),
             ('ja_JP', u'日本語 (Japanese)'),
             ('ko_KO', u'한국어/조선말 (Korean)'),
             ('lv_LV', u'Latviešu (Latvian)'),
             ('lt_LT', u'Lietuvių kalba (Lithuanian)'),
             ('mr_IN', u'मराठी Marāṭhī (Marathi)'),
             ('mn_CN', u'Монгол бичиг (Mongolian)'),
             ('nb_NO', u'Bokmål (Norwegian Bokmal)'),
             ('nn_NO', u'Nynorsk (Norwegian Nynorsk)'),
             ('oc_FR', u"Lenga d'òc (Occitan)"),
             ('pap', 'Papiamentu (Papiamento)'),
             ('fa_IR', u'فارسی (Persian)'),
             ('pl_PL', u'Język polski (Polish)'),
             ('pt_PT', u'Português (Portuguese)'),
             ('ro_RO', u'Română (Romanian)'),
             ('ru_RU', u'Русский (Russian)'),
             ('sk_SK', u'Slovenčina (Slovak)'),
             ('sl_SI', u'Slovenski jezik (Slovene)'),
             ('es_ES', u'Español (Spanish)'),
             ('sv_SE', 'Svenska (Swedish)'),
             ('te_IN', u'తెలుగు (Telugu)'),
             ('th_TH', u'ภาษาไทย (Thai)'),
             ('tr_TR', u'Türkçe (Turkish)'),
             ('uk_UA', u'украї́нська мо́ва (Ukranian)'),
             ('vi_VI', u'tiếng Việt (Vietnamese)')]
        self.addChoiceSetting('view', 'language_set_by_user', _('Language'), 
                              'restart', choices)
        
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

    def ok(self):
        super(LanguagePage, self).ok()
        self.set('view', 'language', self.get('view', 'language_set_by_user'))
        

class TaskAppearancePage(SettingsPage):
    pageName = 'appearance'
    pageTitle = _('Task appearance')
    pageIcon = 'palette_icon'
    
    def __init__(self, *args, **kwargs):
        super(TaskAppearancePage, self).__init__(columns=9, growableColumn=-1, *args, **kwargs)
        self.addAppearanceHeader()
        for setting, label in \
            [('activetasks', _('Active tasks')), 
             ('inactivetasks', _('Inactive tasks')),
             ('completedtasks', _('Completed tasks')),
             ('overduetasks', _('Overdue tasks')),
             ('duesoontasks', _('Tasks due soon'))]:
            self.addLine()
            self.addAppearanceSetting('fgcolor', setting, 
                                      'bgcolor', setting, 
                                      'font', setting, 
                                      'icon', setting, label)
        self.fit()


class FeaturesPage(SettingsPage):
    pageName = 'features'
    pageTitle = _('Features')
    pageIcon = 'cogwheel_icon'
    
    def __init__(self, *args, **kwargs):
        super(FeaturesPage, self).__init__(columns=3, growableColumn=-1, *args, **kwargs)
        self.addBooleanSetting('feature', 'effort', 
            _('Allow for tracking effort'), helpText='restart')
        self.addBooleanSetting('feature', 'notes', _('Allow for taking notes'),
            helpText='restart')
        try:
            import taskcoachlib.syncml.core # pylint: disable-msg=W0404,W0612
        except ImportError:
            pass
        else:
            self.addBooleanSetting('feature', 'syncml', _('Enable SyncML'),
                helpText='restart')
        self.addBooleanSetting('feature', 'iphone', _('Enable iPhone synchronization'),
            helpText='restart')
        self.addIntegerSetting('view', 'efforthourstart',
            _('Hour of start of work day'), minimum=0, maximum=23, helpText=' ')
        self.addIntegerSetting('view', 'efforthourend',
            _('Hour of end of work day'), minimum=1, maximum=24, helpText=' ')
        self.addBooleanSetting('calendarviewer', 'gradient',
            _('Use gradients in calendar views.\nThis may slow down Task Coach.'),
            helpText='restart')
        self.addChoiceSetting('view', 'effortminuteinterval',
            _('Minutes between task start/end times'), ' ',
            [('5', '5'), ('10', '10'), ('15', '15'), ('20', '20'), ('30', '30')])
        self.addIntegerSetting('feature', 'minidletime', _('Minimum idle time'),
            helpText=_('If there is no user input for at least this amount of\nminutes, Task Coach will ask what to do about current efforts.'))
        self.fit()
        

class TaskDatesPage(SettingsPage):
    pageName = 'task'
    pageTitle = _('Task dates')
    pageIcon = 'calendar_icon'
    
    def __init__(self, *args, **kwargs):
        super(TaskDatesPage, self).__init__(columns=4, growableColumn=-1, *args, **kwargs)
        self.addBooleanSetting('behavior', 'markparentcompletedwhenallchildrencompleted',
            _('Mark parent task completed when all children are completed'))
        self.addIntegerSetting('behavior', 'duesoonhours', 
            _("Number of hours that tasks are considered to be 'due soon'"), 
            minimum=0, maximum=9999, flags=(None, wx.ALL|wx.ALIGN_LEFT))
        choices = [('', _('Nothing')),
                   ('startdue', _('Changing the start date changes the due date')),
                   ('duestart', _('Changing the due date changes the start date'))]
        self.addChoiceSetting('view', 'datestied', 
            _('What to do with start and due date if the other one is changed'), 
            '', choices, flags=(None, wx.ALL|wx.ALIGN_LEFT))

        check_choices = [('preset', _('Preset')),
                         ('propose', _('Propose'))]
        day_choices = [('today', _('Today')),
                       ('tomorrow', _('Tomorrow')),
                       ('dayaftertomorrow', _('Day after tomorrow')),
                       ('nextfriday', _('Next Friday')),
                       ('nextmonday', _('Next Monday'))]
        time_choices = [('startofday', _('Start of day')),
                        ('startofworkingday', _('Start of working day')),
                        ('currenttime', _('Current time')),
                        ('endofworkingday', _('End of working day')),
                        ('endofday', _('End of day'))]
        self.addChoiceSetting('view', 'defaultstartdatetime', 
                              _('Default start date and time'), 
                              '', check_choices, day_choices, time_choices)
        self.addChoiceSetting('view', 'defaultduedatetime', 
                              _('Default due date and time'), 
                              '', check_choices, day_choices, time_choices)
        self.addChoiceSetting('view', 'defaultcompletiondatetime', 
                              _('Default completion date and time'),
                              '', [check_choices[1]], day_choices, time_choices)
        self.addChoiceSetting('view', 'defaultreminderdatetime', 
                              _('Default reminder date and time'), 
                              '', check_choices, day_choices, time_choices)
        self.fit()


class TaskReminderPage(SettingsPage):
    pageName = 'reminder'
    pageTitle = _('Task reminders')
    pageIcon = 'clock_alarm_icon'
    
    def __init__(self, *args, **kwargs):
        super(TaskReminderPage, self).__init__(columns=2, growableColumn=-1, *args, **kwargs)
        names = [] # There's at least one, the universal one
        for name in notify.AbstractNotifier.names():
            names.append((name, name))
        self.addChoiceSetting('feature', 'notifier', 
                              _('Notification system to use for reminders'), 
                              '', names, flags=(None, wx.ALL|wx.ALIGN_LEFT))
        snoozeChoices = [(str(choice[0]), choice[1]) for choice in date.snoozeChoices]
        self.addChoiceSetting('view', 'defaultsnoozetime', 
                              _('Default snooze time to use after reminder'), 
                              '', snoozeChoices, flags=(None, wx.ALL|wx.ALIGN_LEFT))
        self.addMultipleChoiceSettings('view', 'snoozetimes', 
            _('Snooze times to offer in task reminder dialog'), 
            date.snoozeChoices[1:], flags=(wx.ALIGN_TOP|wx.ALL, None)) # Don't offer "Don't snooze" as a choice
        self.fit()


class IPhonePage(SettingsPage):
    pageName = 'iphone'
    pageTitle = _('iPhone')
    pageIcon = 'computer_handheld_icon'
    
    def __init__(self, *args, **kwargs):
        super(IPhonePage, self).__init__(columns=3, *args, **kwargs)
        self.addTextSetting('iphone', 'password',
            _('Password for synchronization with iPhone'))
        self.addTextSetting('iphone', 'service',
            _('Bonjour service name'), helpText='restart')
        self.addBooleanSetting('iphone', 'synccompleted',
            _('Upload completed tasks to device'), helpText=_('Upload completed tasks to device'))
        self.addBooleanSetting('iphone', 'showlog',
            _('Show sync log'), helpText=_('Show the synchronization log'))
        self.fit()

        
class EditorPage(SettingsPage):
    pageName = 'editor'
    pageTitle = _('Editor')
    pageIcon = 'edit'
    
    def __init__(self, *args, **kwargs):
        super(EditorPage, self).__init__(columns=2, *args, **kwargs)
        self.addBooleanSetting('editor', 'maccheckspelling',
            _('Check spelling in editors'))
        self.fit()
        
    def ok(self):
        super(EditorPage, self).ok()
        widgets.MultiLineTextCtrl.CheckSpelling = \
            self.settings.getboolean('editor', 'maccheckspelling')


class Preferences(widgets.NotebookDialog):
    allPageNames = ['window', 'save', 'language', 'task', 'reminder', 
                    'appearance', 'features', 'iphone', 'editor']
    pages = dict(window=WindowBehaviorPage, task=TaskDatesPage, 
                 reminder=TaskReminderPage, save=SavePage, 
                 language=LanguagePage, appearance=TaskAppearancePage, 
                 features=FeaturesPage, iphone=IPhonePage, editor=EditorPage)
    
    def __init__(self, settings=None, *args, **kwargs):
        self.settings = settings
        super(Preferences, self).__init__(bitmap='wrench_icon', *args, **kwargs)
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)        
        if '__WXMAC__' in wx.PlatformInfo:
            self.CentreOnParent()

    def addPages(self):
        self._interior.SetMinSize((950, 450))
        for pageName in self.allPageNamesInUserOrder():
            if self.shouldCreatePage(pageName):
                page = self.createPage(pageName)
                self._interior.AddPage(page, page.pageTitle, page.pageIcon)

    def allPageNamesInUserOrder(self):
        ''' Return all pages names in the order stored in the settings. The
            settings may not contain all pages (e.g. because a feature was
            turned off by the user) so we add the missing pages if necessary. '''
        pageNamesInUserOrder = []#self.settings.getlist('editor', 'preferencespages')
        remainingPageNames = self.allPageNames[:]
        for pageName in pageNamesInUserOrder:
            remainingPageNames.remove(pageName)
        return pageNamesInUserOrder + remainingPageNames
                    
    def shouldCreatePage(self, pageName):
        if pageName == 'iphone':
            return self.settings.getboolean('feature', 'iphone')
        elif pageName == 'editor':
            return '__WXMAC__' in wx.PlatformInfo
        else:
            return True

    def createPage(self, pageName):
        return self.pages[pageName](parent=self._interior, settings=self.settings)

    def onClose(self, event):
        event.Skip()
        pageNames = [page.pageName for page in self]
        self.settings.setlist('editor', 'preferencespages', pageNames)
