import wx
import widgets
from i18n import _ 


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
            self.__settings.registerObserver(self.onSettingChanged, 
                'view.%s'%setting)

    def onCheck(self, event):
        checkBox = event.GetEventObject()
        setting = self._checkBoxToSetting[checkBox]
        self.__settings.set('view', setting, str(event.IsChecked()))

    def onSettingChanged(self, notification):
        checkBox = self._settingToCheckBox[notification.option]
        checkBox.SetValue(notification.value == 'True')


class CategoriesFilterPanel(wx.Panel):
    def __init__(self, parent, taskList, settings, *args, **kwargs):
        super(CategoriesFilterPanel, self).__init__(parent, *args, **kwargs)
        self.__taskList = taskList
        self.__settings = settings
        self.createInterior()
        self.layoutInterior()
        self.bindEventHandlers()

    def createInterior(self):
        taskList = self.__taskList
        self._about = widgets.StaticTextWithToolTip(self, 
            label=_('Show tasks that belong to the categories selected below. '
                    'Unselect all categories to reset the filter.') + '\n') 
        self._checkListBox = wx.CheckListBox(self, style=wx.LB_SORT)
        self._checkListBox.InsertItems(list(taskList.categories()), 0)
        for category in taskList.categories():
            if category in taskList.filteredCategories():
                self._checkListBox.Check( \
                    self._checkListBox.FindString(category))
        self._radioBox = wx.RadioBox(self, majorDimension=1, 
            label=_('Show tasks that match'),
            choices=[_('any of the above selected categories'),
                     _('all of the above selected categories')])
        self.setRadioBox()
        self.Enable(len(taskList.categories()) > 0)

    def setRadioBox(self):
        if self.__settings.getboolean('view', 'taskcategoryfiltermatchall'):
            index = 1
        else:
            index = 0
        self._radioBox.SetSelection(index)

    def layoutInterior(self):
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(self._about, flag=wx.EXPAND|wx.ALL, border=5)
        panelSizer.Add(self._checkListBox, proportion=1, flag=wx.EXPAND|wx.ALL, 
            border=5)
        panelSizer.SetItemMinSize(self._checkListBox, (-1, 120))
        panelSizer.Add(self._radioBox, flag=wx.ALL, border=5)
        self.SetSizerAndFit(panelSizer)
        self.GetParent().ResizePanel()

    def bindEventHandlers(self):
        self._checkListBox.Bind(wx.EVT_CHECKLISTBOX, self.onCheckCategory)
        self._radioBox.Bind(wx.EVT_RADIOBOX, self.onCheckMatchAll)
        self.__taskList.registerObserver(self.onAddTask, 'list.add')
        self.__taskList.registerObserver(self.onRemoveTask, 'list.remove')
        self.__settings.registerObserver(self.onMatchAllChanged,
            'view.taskcategoryfiltermatchall')
        self.__taskList.registerObserver(self.onAddCategoryToFilter,
            'filter.category.add')
        self.__taskList.registerObserver(self.onRemoveCategoryFromFilter,
            'filter.category.remove')
        self.__taskList.registerObserver(self.onRemoveAllCategoriesFromFilter,
            'filter.category.removeall')

    def onCheckCategory(self, event):
        category = self._checkListBox.GetString(event.GetInt())
        # Note: using event.IsChecked() would be nicer but doesn't work
        if self._checkListBox.IsChecked(event.GetInt()): 
            self.__taskList.addCategory(category)                
        else:
            self.__taskList.removeCategory(category)

    def onCheckMatchAll(self, event):
        index = event.GetInt()
        setting = ['False', 'True'][index]
        self.__settings.set('view', 'taskcategoryfiltermatchall', setting)

    def onAddTask(self, event):
        for task in event.values():
            task.registerObserver('task.category.add',
                self.onAddCategoryToTask)
            task.registerObserver('task.category.remove',
                self.onRemoveCategoryFromTask)
            for category in task.categories():
                if self._checkListBox.FindString(category) == wx.NOT_FOUND:
                    self._checkListBox.append(category)

    def onRemoveTask(self, event):
        for task in event.values():
            task.removeObservers(self.onAddCategoryToTask, 
                self.onRemoveCategoryFromTask)
            for category in task.categories():
                if category not in self.__taskList.categories():
                    self._checkListBox.Delete(self._checkListBox.FindString(category))
        self.Enable(len(self.__taskList.categories()) > 0)

    def onAddCategoryToTask(self, event):
        for category in event.values():
            if self._checkListBox.FindString(category) == wx.NOT_FOUND:
                self._checkListBox.append(category)
        self.Enable(len(self.__taskList.categories()) > 0)

    def onRemoveCategoryFromTask(self, event):
        for category in event.values():
            if category not in self.__taskList.categories():
                self._checkListBox.Delete(self._checkListBox.FindString(category))
        self.Enable(len(self.__taskList.categories()) > 0)

    def onMatchAllChanged(self, notification):
        self.setRadioBox()

    def onAddCategoryToFilter(self, event):
        category = event.value()
        self._checkListBox.Check(self._checkListBox.FindString(category))

    def onRemoveCategoryFromFilter(self, event):
        category = event.value()
        self._checkListBox.Check(self._checkListBox.FindString(category), 
                                 False)

    def onRemoveAllCategoriesFromFilter(self, event):
        for index in range(self._checkListBox.GetCount()):
            self._checkListBox.Check(index, False)


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
        self.__settings.registerObserver(self.onTasksDueChanged,
            'view.tasksdue')

    def onCheck(self, event):
        value = self.__settingValues[event.GetInt()]
        self.__settings.set('view', 'tasksdue', value)

    def onTasksDueChanged(self, event):
        index = self.__settingValues.index(event.value())
        self._radioBox.SetSelection(index)
