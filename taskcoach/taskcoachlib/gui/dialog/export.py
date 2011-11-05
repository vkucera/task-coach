'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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
from taskcoachlib.i18n import _
from taskcoachlib.widgets import sized_controls
from taskcoachlib import meta


class ExportDialog(sized_controls.SizedDialog):
    ''' Base class for all export dialogs. Use mixin classes below to add
        features. '''

    title = 'Override in subclass'
    section = 'export'
    
    def __init__(self, *args, **kwargs):
        self.window = args[0]
        self.settings = kwargs.pop('settings')
        super(ExportDialog, self).__init__(title=self.title, *args, **kwargs)
        pane = self.GetContentsPane()
        pane.SetSizerType('vertical')
        self.createInterior(pane)
        buttonSizer = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.SetButtonSizer(buttonSizer)
        self.Fit()
        buttonSizer.GetAffirmativeButton().Bind(wx.EVT_BUTTON, self.onOK)
        self.CentreOnParent()

    def createInterior(self, pane):
        raise NotImplementedError
        
    def exportableViewers(self):
        return self.window.viewer
        
    def options(self):
        return dict()

    def onOK(self, event):
        event.Skip()


# Mixin classes for adding behavior to the base export dialog:

class ViewerChooserMixin(object):
    ''' Mixin class for adding a viewer chooser widget to the export dialog. '''
    
    def createViewerChooser(self, pane):
        panel = sized_controls.SizedPanel(pane)
        panel.SetSizerType('horizontal')
        label = wx.StaticText(panel, label=_('Export items from:'))
        label.SetSizerProps(valign='center')
        # pylint: disable-msg=W0201
        self.viewerComboBox = wx.ComboBox(panel, style=wx.CB_READONLY|wx.CB_SORT)
        self.titleToViewer = dict()
        for viewer in self.exportableViewers():
            self.viewerComboBox.Append(viewer.title()) # pylint: disable-msg=E1101
            # Would like to user client data in the combobox, but that 
            # doesn't work on all platforms
            self.titleToViewer[viewer.title()] = viewer
        selectedViewer = self.window.viewer.activeViewer()
        if selectedViewer not in self.exportableViewers():
            selectedViewer = self.exportableViewers()[0]
        self.viewerComboBox.SetValue(selectedViewer.title())
        self.viewerComboBox.Bind(wx.EVT_COMBOBOX, self.onViewerChanged)       

    def selectedViewer(self):
        return self.titleToViewer[self.viewerComboBox.GetValue()]

    def onViewerChanged(self, event):
        ''' Override to react to a different viewer being picked by the user.
            For example, change the columns available for export. '''
        event.Skip()
            

class SelectionOnlyChooserMixin(object):  
    ''' Mixin class for adding a widget to the export dialog that lets the
        user choose between exporting all items or just the selected items. '''
    
    selectionOnlySetting = 'Override in subclass'
      
    def createSelectionOnlyChooser(self, pane):
        self.selectionOnlyCheckBox = wx.CheckBox(pane, # pylint: disable-msg=W0201
            label=_('Export only the selected items'))
        selectionOnly = self.settings.getboolean(self.section, 
            self.selectionOnlySetting)
        self.selectionOnlyCheckBox.SetValue(selectionOnly)

    def selectionOnly(self):
        return self.selectionOnlyCheckBox.GetValue()

    def options(self):
        options = super(SelectionOnlyChooserMixin, self).options()
        options['selectionOnly'] = self.selectionOnly()
        return options

    def onOK(self, event):
        super(SelectionOnlyChooserMixin, self).onOK(event)
        self.settings.set(self.section, self.selectionOnlySetting, # pylint: disable-msg=E1101
                          str(self.selectionOnly()))    


class ColumnPickerMixin(object):
    ''' Mixin class for adding a widget that lets the user select which columns
        should be used for exporting. '''

    def createColumnPicker(self, pane):
        panel = sized_controls.SizedPanel(pane)
        panel.SetSizerType('horizontal')
        panel.SetSizerProps(expand=True, proportion=1)
        label = wx.StaticText(panel, label=_('Columns to export:'))
        label.SetSizerProps(valign='top')
        self.columnPicker = wx.CheckListBox(panel) # pylint: disable-msg=W0201
        self.columnPicker.SetSizerProps(expand=True, proportion=1)
        self.populateColumnPicker()
        
    def populateColumnPicker(self):
        self.emptyColumnPicker()
        self.fillColumnPicker()

    def emptyColumnPicker(self):
        while not self.columnPicker.IsEmpty():
            self.columnPicker.Delete(0)
                    
    def fillColumnPicker(self):
        selectedViewer = self.selectedViewer()
        if not selectedViewer.hasHideableColumns():
            return
        visibleColumns = selectedViewer.visibleColumns()
        for column in selectedViewer.columns():
            if column.header():
                index = self.columnPicker.Append(column.header(), clientData=column)
                self.columnPicker.Check(index, column in visibleColumns)
            
    def columns(self):
        indices = [index for index in range(self.columnPicker.GetCount()) if self.columnPicker.IsChecked(index)]
        return [self.columnPicker.GetClientData(index) for index in indices]

    def options(self):
        options = super(ColumnPickerMixin, self).options()
        options['columns'] = self.columns()
        return options

    def onViewerChanged(self, event):
        super(ColumnPickerMixin, self).onViewerChanged(event)
        self.populateColumnPicker()


class SeparateDateAndTimeColumnsMixin(object):
    ''' Mixin class for adding a widget that lets the user decide whether
        dates and times should be separated or kept together. '''
    
    separateDateAndTimeColumnsSetting = 'Override in subclass'

    def createSeparateDateAndTimeColumnsCheckBox(self, pane):
        self.separateDateAndTimeColumnsCheckBox = wx.CheckBox(pane, # pylint: disable-msg=W0201
            label=_('Put dates and times in separate columns'))
        separateDateAndTimeColumns = self.settings.getboolean(self.section,
            self.separateDateAndTimeColumnsSetting)
        self.separateDateAndTimeColumnsCheckBox.SetValue(separateDateAndTimeColumns)

    def separateDateAndTimeColumns(self):
        return self.separateDateAndTimeColumnsCheckBox.GetValue()
    
    def options(self):
        options = super(SeparateDateAndTimeColumnsMixin, self).options()
        options['separateDateAndTimeColumns'] = self.separateDateAndTimeColumns()
        return options

    def onOK(self, event):
        super(SeparateDateAndTimeColumnsMixin, self).onOK(event)
        self.settings.setboolean(self.section, self.separateDateAndTimeColumnsSetting, 
                                 self.separateDateAndTimeColumns())
        

class SeparateCSSChooserMixin(object):
    ''' Mixin class to let the user write CSS style information to a 
        separate file instead of including it into the HTML file. '''
    
    separateCSSSetting = 'Override in subclass'

    def createSeparateCSSChooser(self, pane):        
        self.separateCSSCheckBox = wx.CheckBox(pane, # pylint: disable-msg=W0201
            label=_('Write style information to a separate CSS file'))
        width = max([child.GetSize()[0] for child in pane.GetChildren()])
        info = wx.StaticText(pane, 
            label=_('If a CSS file exists for the exported file, %(name)s will not overwrite it. ' \
                    'This allows you to change the style information without losing your changes on the next export.')%meta.metaDict)
        info.Wrap(width)
        separateCSS = self.settings.getboolean(self.section, 
                                               self.separateCSSSetting)
        self.separateCSSCheckBox.SetValue(separateCSS)
    
    def separateCSS(self):
        return self.separateCSSCheckBox.GetValue()
    
    def options(self):
        options = super(SeparateCSSChooserMixin, self).options()
        options['separateCSS'] = self.separateCSS()
        return options
        
    def onOK(self, event):
        super(SeparateCSSChooserMixin, self).onOK(event)
        self.settings.set(self.section, self.separateCSSSetting, 
                          str(self.separateCSS()))
        

# Export dialogs for different file types:

class ExportAsCSVDialog(ColumnPickerMixin, ViewerChooserMixin, 
                        SelectionOnlyChooserMixin, 
                        SeparateDateAndTimeColumnsMixin, ExportDialog):
    title = _('Export as CSV')
    selectionOnlySetting = 'csv_selectiononly'
    separateDateAndTimeColumnsSetting = 'csv_separatedateandtimecolumns'
    
    def createInterior(self, pane):
        self.createViewerChooser(pane)
        self.createColumnPicker(pane)
        self.createSelectionOnlyChooser(pane)
        self.createSeparateDateAndTimeColumnsCheckBox(pane)
        
          
class ExportAsICalendarDialog(ViewerChooserMixin, SelectionOnlyChooserMixin, 
                              ExportDialog):
    title = _('Export as iCalendar')
    selectionOnlySetting = 'ical_selectiononly'
    
    def createInterior(self, pane):
        self.createViewerChooser(pane)
        self.createSelectionOnlyChooser(pane)

    def exportableViewers(self):
        viewers = super(ExportAsICalendarDialog, self).exportableViewers()
        return [viewer for viewer in viewers if
                viewer.isShowingTasks() or 
                (viewer.isShowingEffort() and not viewer.isShowingAggregatedEffort())]


class ExportAsHTMLDialog(ColumnPickerMixin, ViewerChooserMixin,
                         SelectionOnlyChooserMixin, SeparateCSSChooserMixin, 
                         ExportDialog):
    title = _('Export as HTML')
    selectionOnlySetting = 'html_selectiononly'
    separateCSSSetting = 'html_separatecss'
    
    def createInterior(self, pane):
        self.createViewerChooser(pane)
        self.createColumnPicker(pane)
        self.createSelectionOnlyChooser(pane)
        self.createSeparateCSSChooser(pane)
                

class ExportAsTodoTxtDialog(ViewerChooserMixin, SelectionOnlyChooserMixin, 
                            ExportDialog):
    title = _('Export as Todo.txt')
    selectionOnlySetting = 'todotxt_selectiononly'
    
    def createInterior(self, pane):
        self.createViewerChooser(pane)
        self.createSelectionOnlyChooser(pane)
    
    def exportableViewers(self):
        viewers = super(ExportAsTodoTxtDialog, self).exportableViewers()
        return [viewer for viewer in viewers if viewer.isShowingTasks()]
    