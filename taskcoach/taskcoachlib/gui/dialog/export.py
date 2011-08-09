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
    title = 'Override in subclass'
    section = 'export'
    selectionOnlySetting = 'Override in subclass'

    
    def __init__(self, *args, **kwargs):
        self.window = args[0]
        self.settings = kwargs.pop('settings')
        super(ExportDialog, self).__init__(title=self.title, *args, **kwargs)
        pane = self.GetContentsPane()
        pane.SetSizerType("vertical")
        self.createInterior(pane)
        buttonSizer = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.SetButtonSizer(buttonSizer)
        self.Fit()
        buttonSizer.GetAffirmativeButton().Bind(wx.EVT_BUTTON, self.onOK)

    def createInterior(self, pane):
        self.createViewerChooser(pane)
        self.createSelectionOnlyChooser(pane)

    def createViewerChooser(self, pane):
        panel = sized_controls.SizedPanel(pane)
        panel.SetSizerType('horizontal')
        label = wx.StaticText(panel, label=('Export items from:'))
        sized_controls.SetSizerProp(label, 'valign', 'center')
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
        panel.Fit()
        
    def exportableViewers(self):
        return self.window.viewer
        
    def createSelectionOnlyChooser(self, pane):
        self.selectionOnlyCheckBox = wx.CheckBox(pane, # pylint: disable-msg=W0201
            label=_('Export only the selected items'))
        selectionOnly = self.settings.getboolean(self.section, 
            self.selectionOnlySetting)
        self.selectionOnlyCheckBox.SetValue(selectionOnly)

    def selectionOnly(self):
        return self.selectionOnlyCheckBox.GetValue()
    
    def options(self):
        return dict(selectionOnly=self.selectionOnly())
    
    def selectedViewer(self):
        return self.titleToViewer[self.viewerComboBox.GetValue()]

    def onOK(self, event):
        self.settings.set(self.section, self.selectionOnlySetting, # pylint: disable-msg=E1101
                          str(self.selectionOnly()))
        event.Skip()
            

class ExportAsCSVDialog(ExportDialog):
    title = _('Export as CSV')
    selectionOnlySetting = 'csv_selectiononly'


class ExportAsICalendarDialog(ExportDialog):
    title = _('Export as iCalendar')
    selectionOnlySetting = 'ical_selectiononly'
    
    def exportableViewers(self):
        viewers = super(ExportAsICalendarDialog, self).exportableViewers()
        return [viewer for viewer in viewers if
                viewer.isShowingTasks() or 
                (viewer.isShowingEffort() and not viewer.isShowingAggregatedEffort())]
    

class ExportAsHTMLDialog(ExportDialog):
    title = _('Export as HTML')
    selectionOnlySetting = 'html_selectiononly'
    separateCSSSetting = 'html_separatecss'
    
    def createInterior(self, pane):
        super(ExportAsHTMLDialog, self).createInterior(pane)
        self.createSeparateCSSChooser(pane)
                
    def createSeparateCSSChooser(self, pane):        
        self.separateCSSCheckBox = wx.CheckBox(pane, # pylint: disable-msg=W0201
            label=_('Write style information to a separate CSS file'))
        width = max(self.separateCSSCheckBox.GetSize()[0],
                    self.selectionOnlyCheckBox.GetSize()[0],
                    self.viewerComboBox.GetSize()[0])
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
        options = super(ExportAsHTMLDialog, self).options()
        options['separateCSS'] = self.separateCSS()
        return options
        
    def onOK(self, event):
        super(ExportAsHTMLDialog, self).onOK(event)
        self.settings.set(self.section, self.separateCSSSetting, 
                          str(self.separateCSS()))
