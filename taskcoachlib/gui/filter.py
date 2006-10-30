import wx
import widgets, patterns
from i18n import _ 
try:
    import wx.lib.customtreectrl as customtree # for wxPython >= 2.7.1
except:
    import thirdparty.CustomTreeCtrl as customtree # for wxPython < 2.7.1
import domain.category as category

class SubjectFilterPanel(wx.Panel):
    def __init__(self, parent, viewer, settings, *args, **kwargs):
        super(SubjectFilterPanel, self).__init__(parent, *args, **kwargs)
        self.__viewer = viewer
        self.__settings = settings
        self.createInterior()
        self.layoutInterior()
        self.bindEventHandlers()
        
    def createInterior(self):
        self.__timer = wx.Timer(self)
        self._about = widgets.StaticTextWithToolTip(self, label= \
            _('Type a search string (a regular expression) ' 
              'and press enter.') + '\n')
        self._about.SetBackgroundColour(self.GetBackgroundColour())
        searchString = self.__settings.get('view', 'tasksearchfilterstring')
        self._subjectEntry = widgets.SingleLineTextCtrl(self, searchString,
            style=wx.TE_PROCESS_ENTER)
        self._caseCheckBox = wx.CheckBox(self, label=_('Match case'))
        self._clearButton = wx.Button(self, label=_('Clear'))

    def bindEventHandlers(self):
        for eventSource, eventType, eventHandler in \
            [(self, wx.EVT_TIMER, self.onFind),
             (self._subjectEntry, wx.EVT_TEXT_ENTER, self.onFind),
             (self._subjectEntry, wx.EVT_TEXT, self.onFindLater),
             (self._caseCheckBox, wx.EVT_CHECKBOX, self.onFind),
             (self._clearButton, wx.EVT_BUTTON, self.clear)]:
            eventSource.Bind(eventType, eventHandler)
        
    def layoutInterior(self):
        verticalSizer = wx.BoxSizer(wx.VERTICAL)
        self._about.SetMinSize((1,-1))
        verticalSizer.Add(self._about, flag=wx.EXPAND|wx.ALL, border=5)
        verticalSizer.Add(self._subjectEntry, flag=wx.EXPAND|wx.ALL, 
            border=5)
        horizontalSizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontalSizer.Add(self._caseCheckBox,
            flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5)
        horizontalSizer.Add((1,1), flag=wx.EXPAND, proportion=1)
        horizontalSizer.Add(self._clearButton,
            flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, border=5)
        verticalSizer.Add(horizontalSizer, flag=wx.EXPAND)
        self.SetSizerAndFit(verticalSizer)        

    def onFindLater(self, event):
        # Start the timer so that the actual filtering will be done
        # only when the user pauses typing (at least 0.5 second)
        self.__timer.Start(500, oneShot=True)

    def onFind(self, event):
        if self.__timer.IsRunning():
            self.__timer.Stop()
        searchString = self._subjectEntry.GetValue()
        self.__settings.set('view', 'tasksearchfilterstring', searchString)
        self.__settings.set('view', 'tasksearchfiltermatchcase', 
            str(self._caseCheckBox.GetValue()))
        if searchString:
            self.__viewer.expandAll()

    def clear(self, event=None):
        self._subjectEntry.SetValue('')
        self.onFind(event)


class StatusFilterPanel(wx.Panel):
    def __init__(self, parent, taskList, settings, *args, **kwargs):
        super(StatusFilterPanel, self).__init__(parent, *args, **kwargs)
        self.__taskList = taskList
        self.__settings = settings
        self.createInterior()
        self.layoutInterior()
        self.bindEventHandlers()

    def createInterior(self):
        self.labelsAndSettings = [(_('Active tasks'), 'activetasks'),
                                  (_('Inactive tasks'), 'inactivetasks'),
                                  (_('Completed tasks'), 'completedtasks'),
                                  (_('Over due tasks'), 'overduetasks'),
                                  (_('Over budget tasks'), 'overbudgettasks')]
        self._checkBoxToSetting = {}
        self._settingToCheckBox = {}
        self._checkBoxes = []
        for label, setting in self.labelsAndSettings:
            checkBox = wx.CheckBox(self, label=label)
            checkBox.SetValue(self.__settings.getboolean('view', setting))
            self._checkBoxToSetting[checkBox] = setting
            self._settingToCheckBox[setting] = checkBox
            self._checkBoxes.append(checkBox)

    def layoutInterior(self):
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        for checkBox in self._checkBoxes:
            panelSizer.Add(checkBox, flag=wx.ALL, border=5)
        self.SetSizerAndFit(panelSizer)

    def bindEventHandlers(self):
        for checkBox in self._checkBoxes:
            checkBox.Bind(wx.EVT_CHECKBOX, self.onCheck)
        for label, setting in self.labelsAndSettings:
            patterns.Publisher().registerObserver(self.onSettingChanged, 
                eventType='view.%s'%setting)

    def onCheck(self, event):
        checkBox = event.GetEventObject()
        setting = self._checkBoxToSetting[checkBox]
        self.__settings.set('view', setting, str(event.IsChecked()))

    def onSettingChanged(self, event):
        checkBox = self._settingToCheckBox[event.type().split('.')[1]]
        checkBox.SetValue(event.value() == 'True')


class CategoriesFilterPanel(wx.Panel):
    def __init__(self, parent, categories, settings, *args, **kwargs):
        super(CategoriesFilterPanel, self).__init__(parent, *args, **kwargs)
        self.__categories = category.CategorySorter(categories)
        self.__settings = settings
        self.createInterior()
        self.layoutInterior()
        self.bindEventHandlers()

    def createInterior(self):
        self._about = widgets.StaticTextWithToolTip(self, 
            label=_('Show tasks that belong to the categories selected below. '
                    'Unselect all categories to reset the filter.') + '\n') 
        self._treeCtrl = widgets.CheckTreeCtrl(self, 
            lambda index: self.__categories[index].subject(),
            lambda index: (-1, -1), lambda index: customtree.TreeItemAttr(),
            lambda index: id(self.__categories[index]), 
            lambda: sorted([index for index in range(len(self.__categories)) if \
                     self.__categories[index] in self.__categories.rootItems()]),
            lambda parentIndex: [index for index in range(len(self.__categories)) if \
                     self.__categories[index] in self.__categories[parentIndex].children()], 
            lambda index: self.__categories[index].isFiltered(),
            lambda *args: None, lambda *args: None,
            lambda *args: None)
        self._radioBox = wx.RadioBox(self, majorDimension=1, 
            label=_('Show tasks that match'),
            choices=[_('any of the above selected categories'),
                     _('all of the above selected categories')])
        self.setRadioBox()
        self.Enable(len(self.__categories) > 0)

    def setRadioBox(self):
        if self.__settings.getboolean('view', 'taskcategoryfiltermatchall'):
            index = 1
        else:
            index = 0
        self._radioBox.SetSelection(index)

    def layoutInterior(self):
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(self._about, flag=wx.EXPAND|wx.ALL, border=5)
        panelSizer.Add(self._treeCtrl, proportion=1, flag=wx.EXPAND|wx.ALL, 
            border=5)
        panelSizer.SetItemMinSize(self._treeCtrl, (-1, 120))
        panelSizer.Add(self._radioBox, flag=wx.ALL, border=5)
        self.SetSizerAndFit(panelSizer)
        self.GetParent().ResizePanel()

    def bindEventHandlers(self):
        self._treeCtrl.Bind(customtree.EVT_TREE_ITEM_CHECKED, self.onCheckCategory)
        self._radioBox.Bind(wx.EVT_RADIOBOX, self.onCheckMatchAll)
        patterns.Publisher().registerObserver(self.onMatchAllChanged,
            'view.taskcategoryfiltermatchall')
        patterns.Publisher().registerObserver(self.onFilteredCategoriesChanged, 
            'category.filter')
        patterns.Publisher().registerObserver(self.onAddCategory,
            self.__categories.addItemEventType())
        patterns.Publisher().registerObserver(self.onRemoveCategory,
            self.__categories.removeItemEventType())
        patterns.Publisher().registerObserver(self.onCategorySubjectChanged,
            category.Category.subjectChangedEventType())
        patterns.Publisher().registerObserver(self.onCategorySubjectChanged,
            self.__categories.sortEventType())
        
    def onCheckCategory(self, event):
        category = self.__categories[self._treeCtrl.index(event.GetItem())]
        category.setFiltered(event.GetItem().IsChecked())

    def onCheckMatchAll(self, event):
        index = event.GetInt()
        setting = ['False', 'True'][index]
        self.__settings.set('view', 'taskcategoryfiltermatchall', setting)

    def onAddCategory(self, event):
        self._treeCtrl.refresh(len(self.__categories))
        self.Enable(len(self.__categories) > 0)

    def onRemoveCategory(self, event):
        self._treeCtrl.refresh(len(self.__categories))
        self.Enable(len(self.__categories) > 0)

    def onMatchAllChanged(self, notification):
        self.setRadioBox()

    def onFilteredCategoriesChanged(self, event):
        self._treeCtrl.refresh(len(self.__categories))
        
    def onCategorySubjectChanged(self, event):
        self._treeCtrl.refresh(len(self.__categories))

    
class DueDateFilterPanel(wx.Panel):
    def __init__(self, parent, settings, *args, **kwargs):
        super(DueDateFilterPanel, self).__init__(parent, *args, **kwargs)
        self.__settings = settings
        self.__settingValues = ['Today', 'Tomorrow', 'Workweek', 'Week', 
                                'Month', 'Year', 'Unlimited']
        self.createInterior()
        self.layoutInterior()
        self.bindEventHandlers()

    def createInterior(self):
        self._radioBox = wx.RadioBox(self, majorDimension=1, 
            label=_('Show tasks due before'),
            choices=[_('&Today'),
                     _('T&omorrow'),
                     _('Wo&rkweek'),
                     _('&Week'),
                     _('&Month'),
                     _('&Year'),
                     _('&Unlimited')])
        value = self.__settings.get('view', 'tasksdue')
        index = self.__settingValues.index(value)
        self._radioBox.SetSelection(index)

    def layoutInterior(self):
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(self._radioBox, flag=wx.EXPAND|wx.ALL, border=5)
        self.SetSizerAndFit(panelSizer)

    def bindEventHandlers(self):
        self._radioBox.Bind(wx.EVT_RADIOBOX, self.onCheck)
        patterns.Publisher().registerObserver(self.onTasksDueChanged,
            eventType='view.tasksdue')

    def onCheck(self, event):
        value = self.__settingValues[event.GetInt()]
        self.__settings.set('view', 'tasksdue', value)

    def onTasksDueChanged(self, event):
        index = self.__settingValues.index(event.value())
        self._radioBox.SetSelection(index)
