'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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

import wx, uicommand
from taskcoachlib import operating_system, widgets
from taskcoachlib.thirdparty import aui
from taskcoachlib.thirdparty import hypertreelist as htl
from taskcoachlib.help.balloontips import BalloonTipManager
from taskcoachlib.i18n import _


class _AutoWidthTree(widgets.autowidth.AutoColumnWidthMixin, htl.HyperTreeList):
    def __init__(self, *args, **kwargs):
        super(_AutoWidthTree, self).__init__(*args, **kwargs)
        self.ToggleAutoResizing(True)

    def _get_MainWindow(self):
        return self.GetMainWindow()
    MainWindow = property(_get_MainWindow)


class _ToolBarEditorInterior(wx.Panel):
    def __init__(self, toolbar, settings, parent):
        self.__toolbar = toolbar
        self.__visible = toolbar.visibleUICommands()

        super(_ToolBarEditorInterior, self).__init__(parent)

        vsizer = wx.BoxSizer(wx.VERTICAL)

        # Toolbar preview
        sb = wx.StaticBox(self, wx.ID_ANY, _('Preview'))
        self.__preview = ToolBar(self, settings, self.__toolbar.GetToolBitmapSize())
        sbsz = wx.StaticBoxSizer(sb)
        sbsz.Add(self.__preview, 1)
        vsizer.Add(sbsz, 0, wx.EXPAND|wx.ALL, 3)
        self.__HackPreview()

        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.__imgList = wx.ImageList(16, 16)
        self.__imgListIndex = dict()
        empty = wx.EmptyImage(16, 16)
        empty.Replace(0, 0, 0, 255, 255, 255)
        self.__imgListIndex['nobitmap'] = self.__imgList.Add(empty.ConvertToBitmap())
        for uiCommand in toolbar.uiCommands():
            if uiCommand is not None and not isinstance(uiCommand, int) and uiCommand.bitmap != 'nobitmap':
                self.__imgListIndex[uiCommand.bitmap] = self.__imgList.Add(wx.ArtProvider.GetBitmap(uiCommand.bitmap, wx.ART_MENU, (16, 16)))

        # Remaining commands list
        sb = wx.StaticBox(self, wx.ID_ANY, _('Commands'))
        self.__remainingCommands = _AutoWidthTree(self,
                    agwStyle=htl.TR_NO_BUTTONS|htl.TR_SINGLE|htl.TR_NO_LINES|htl.TR_HIDE_ROOT|htl.TR_NO_HEADER|htl.TR_FULL_ROW_HIGHLIGHT)
        self.__remainingCommands.AddColumn('Command')
        self.__remainingCommands.SetImageList(self.__imgList)

        sbsz = wx.StaticBoxSizer(sb)
        sbsz.Add(self.__remainingCommands, 1, wx.EXPAND)
        hsizer.Add(sbsz, 1, wx.EXPAND|wx.ALL, 3)

        self.__PopulateRemainingCommands()

        # Show/hide buttons
        btnSizer = wx.BoxSizer(wx.VERTICAL)
        self.__showButton = wx.BitmapButton(self, wx.ID_ANY, wx.ArtProvider.GetBitmap('next', wx.ART_BUTTON, (16, 16)))
        self.__showButton.Enable(False)
        btnSizer.Add(self.__showButton, wx.ALL, 3)
        self.__hideButton = wx.BitmapButton(self, wx.ID_ANY, wx.ArtProvider.GetBitmap('prev', wx.ART_BUTTON, (16, 16)))
        self.__hideButton.Enable(False)
        btnSizer.Add(self.__hideButton, wx.ALL, 3)
        hsizer.Add(btnSizer, 0, wx.ALIGN_CENTRE)

        # Visible commands list
        sb = wx.StaticBox(self, wx.ID_ANY, _('Visible commands'))
        self.__visibleCommands = _AutoWidthTree(self,
                    agwStyle=htl.TR_NO_BUTTONS|htl.TR_SINGLE|htl.TR_NO_LINES|htl.TR_HIDE_ROOT|htl.TR_NO_HEADER|htl.TR_FULL_ROW_HIGHLIGHT)
        self.__visibleCommands.AddColumn('Command')
        self.__visibleCommands.SetImageList(self.__imgList)

        sbsz = wx.StaticBoxSizer(sb)
        sbsz.Add(self.__visibleCommands, 1, wx.EXPAND)
        hsizer.Add(sbsz, 1, wx.EXPAND|wx.ALL, 3)

        # Move buttons
        btnSizer = wx.BoxSizer(wx.VERTICAL)
        self.__moveUpButton = wx.BitmapButton(self, wx.ID_ANY, wx.ArtProvider.GetBitmap('up', wx.ART_BUTTON, (16, 16)))
        self.__moveUpButton.Enable(False)
        btnSizer.Add(self.__moveUpButton, wx.ALL, 3)
        self.__moveDownButton = wx.BitmapButton(self, wx.ID_ANY, wx.ArtProvider.GetBitmap('down', wx.ART_BUTTON, (16, 16)))
        self.__moveDownButton.Enable(False)
        btnSizer.Add(self.__moveDownButton, wx.ALL, 3)
        hsizer.Add(btnSizer, 0, wx.ALIGN_CENTRE)

        self.__PopulateVisibleCommands()

        vsizer.Add(hsizer, 1, wx.EXPAND|wx.ALL, 3)
        self.SetSizer(vsizer)

        self.__remainingSelection = None
        self.__visibleSelection = None
        self.__draggedItem = None
        self.__draggingFromAvailable = False
        wx.EVT_TREE_SEL_CHANGED(self.__remainingCommands, wx.ID_ANY, self.__OnRemainingSelectionChanged)
        wx.EVT_TREE_SEL_CHANGED(self.__visibleCommands, wx.ID_ANY, self.__OnVisibleSelectionChanged)
        wx.EVT_BUTTON(self.__hideButton, wx.ID_ANY, self.__OnHide)
        wx.EVT_BUTTON(self.__showButton, wx.ID_ANY, self.__OnShow)
        wx.EVT_BUTTON(self.__moveUpButton, wx.ID_ANY, self.__OnMoveUp)
        wx.EVT_BUTTON(self.__moveDownButton, wx.ID_ANY, self.__OnMoveDown)
        wx.EVT_TREE_BEGIN_DRAG(self.__visibleCommands, wx.ID_ANY, self.__OnBeginDrag)
        wx.EVT_TREE_END_DRAG(self.__visibleCommands, wx.ID_ANY, self.__OnEndDrag)
        wx.EVT_TREE_BEGIN_DRAG(self.__remainingCommands, wx.ID_ANY, self.__OnBeginDrag2)

        wx.CallAfter(wx.GetTopLevelParent(self).AddBalloonTip, settings, 'customizabletoolbars_dnd', self.__visibleCommands,
                  title=_('Drag and drop'), message=_('''Reorder toolbar buttons by drag and dropping them in this list.'''))

    def __OnRemainingSelectionChanged(self, event):
        self.__remainingSelection = event.GetItem()
        self.__showButton.Enable(self.__remainingSelection is not None)
        event.Skip()

    def __OnVisibleSelectionChanged(self, event):
        self.__visibleSelection = event.GetItem()
        self.__hideButton.Enable(self.__visibleSelection is not None)
        items = self.__visibleCommands.GetRootItem().GetChildren()
        idx = items.index(event.GetItem())
        self.__moveUpButton.Enable(idx != 0)
        self.__moveDownButton.Enable(idx != len(items) - 1)
        event.Skip()

    def __OnHide(self, event):
        idx = self.__visibleCommands.GetRootItem().GetChildren().index(self.__visibleSelection)
        uiCommand = self.__visibleCommands.GetItemPyData(self.__visibleSelection)
        self.__visibleCommands.Delete(self.__visibleSelection)
        self.__visibleSelection = None
        self.__hideButton.Enable(False)
        del self.__visible[idx]
        if isinstance(uiCommand, uicommand.UICommand):
            for child in self.__remainingCommands.GetRootItem().GetChildren()[2:]:
                if self.__remainingCommands.GetItemPyData(child) == uiCommand:
                    self.__remainingCommands.EnableItem(child, True)
                    break
        self.__HackPreview()

    def __OnShow(self, event):
        uiCommand = self.__remainingCommands.GetItemPyData(self.__remainingSelection)
        if uiCommand is None:
            item = self.__visibleCommands.AppendItem(self.__visibleCommands.GetRootItem(), _('Separator'))
        elif isinstance(uiCommand, int):
            item = self.__visibleCommands.AppendItem(self.__visibleCommands.GetRootItem(), _('Spacer'))
        else:
            item = self.__visibleCommands.AppendItem(self.__visibleCommands.GetRootItem(), uiCommand.getHelpText())
            self.__visibleCommands.SetItemImage(item, self.__imgListIndex.get(uiCommand.bitmap, -1))
        self.__visibleCommands.SetItemPyData(item, uiCommand)
        self.__visible.append(uiCommand)
        if isinstance(uiCommand, uicommand.UICommand):
            self.__remainingCommands.EnableItem(self.__remainingSelection, False)
            self.__remainingSelection = None
            self.__showButton.Enable(False)
        self.__HackPreview()

    def __Swap(self, delta):
        items = self.__visibleCommands.GetRootItem().GetChildren()
        index = items.index(self.__visibleSelection)
        text = self.__visibleSelection.GetText()
        data = self.__visibleSelection.GetData()
        self.__visibleCommands.Delete(self.__visibleSelection)
        item = self.__visibleCommands.InsertItem(self.__visibleCommands.GetRootItem(), index + delta, text)
        self.__visibleCommands.SetItemPyData(item, data)
        if isinstance(data, uicommand.UICommand):
            self.__visibleCommands.SetItemImage(item, self.__imgListIndex.get(data.bitmap, -1))
        self.__visibleCommands.SelectItem(item)
        self.__visible[index], self.__visible[index + delta] = self.__visible[index + delta], self.__visible[index]
        self.__HackPreview()

    def __OnMoveUp(self, event):
        self.__Swap(-1)

    def __OnMoveDown(self, event):
        self.__Swap(1)

    def __OnBeginDrag2(self, event):
        self.__draggingFromAvailable = True
        event.Veto()

    def __OnBeginDrag(self, event):
        if self.__draggingFromAvailable or event.GetItem() == self.__visibleCommands.GetRootItem():
            event.Veto()
        else:
            self.__draggedItem = event.GetItem()
            event.Allow()
        self.__draggingFromAvailable = False

    def __OnEndDrag(self, event):
        if event.GetItem() is not None and event.GetItem() != self.__draggedItem:
            targetItem = event.GetItem()
            sourceIndex = self.__visibleCommands.GetRootItem().GetChildren().index(self.__draggedItem)
            uiCommand = self.__visible[sourceIndex]
            self.__visibleCommands.Delete(self.__draggedItem)
            del self.__visible[sourceIndex]
            targetIndex = self.__visibleCommands.GetRootItem().GetChildren().index(targetItem) + 1
            if targetItem.PartialHilight() & wx.wx.TREE_HITTEST_ONITEMUPPERPART:
                targetIndex -= 1
            self.__visible.insert(targetIndex, uiCommand)
            if uiCommand is None:
                text = _('Separator')
                img = -1
            elif isinstance(uiCommand, int):
                text = _('Spacer')
                img = -1
            else:
                text = uiCommand.getHelpText()
                img = self.__imgListIndex.get(uiCommand.bitmap, -1)
            item = self.__visibleCommands.InsertItem(self.__visibleCommands.GetRootItem(), targetIndex, text)
            self.__visibleCommands.SetItemPyData(item, uiCommand)
            self.__visibleCommands.SetItemImage(item, img)
            self.__HackPreview()
        self.__draggedItem = None

    def __HackPreview(self):
        self.__preview.loadPerspective(self.getToolBarPerspective(), customizable=False)
        for uiCommand in self.__preview.visibleUICommands():
            if uiCommand is not None and not isinstance(uiCommand, int):
                uiCommand.unbind(self.__preview, uiCommand.id)
                self.__preview.EnableTool(uiCommand.id, True)

    def __Populate(self, tree, uiCommands, enableCallback):
        tree.Freeze()
        try:
            tree.DeleteAllItems()
            root = tree.AddRoot('Root')

            for uiCommand in uiCommands:
                if uiCommand is None:
                    text = _('Separator')
                elif isinstance(uiCommand, int):
                    text = _('Spacer')
                else:
                    text = uiCommand.getHelpText()

                item = tree.AppendItem(root, text)
                if uiCommand is not None and not isinstance(uiCommand, int):
                    tree.SetItemImage(item, self.__imgListIndex.get(uiCommand.bitmap, -1))
                    tree.EnableItem(item, enableCallback(uiCommand))
                tree.SetItemPyData(item, uiCommand)
        finally:
            tree.Thaw()

    def __PopulateRemainingCommands(self):
        def enableCallback(uiCommand):
            if isinstance(uiCommand, uicommand.UICommand):
                return uiCommand not in self.__visible
            return True
        self.__Populate(self.__remainingCommands,
                        [None, 1] + [uiCommand for uiCommand in self.createToolBarUICommands() if isinstance(uiCommand, uicommand.UICommand)], enableCallback)

    def __PopulateVisibleCommands(self):
        self.__Populate(self.__visibleCommands, self.__visible, lambda x: True)

    def getToolBarPerspective(self):
        names = list()
        for uiCommand in self.__visible:
            if uiCommand is None:
                names.append('Separator')
            elif isinstance(uiCommand, int):
                names.append('Spacer')
            else:
                names.append(uiCommand.uniqueName())
        return ','.join(names)

    def createToolBarUICommands(self):
        return self.__toolbar.uiCommands()


class ToolBarEditor(BalloonTipManager, widgets.Dialog):
    def __init__(self, toolbar, settings, *args, **kwargs):
        self.__toolbar = toolbar
        self.__settings = settings
        super(ToolBarEditor, self).__init__(*args, **kwargs)

    def createInterior(self):
        return _ToolBarEditorInterior(self.__toolbar, self.__settings, self._panel)

    def ok(self, event=None):
        self.__toolbar.savePerspective(self._interior.getToolBarPerspective())
        super(ToolBarEditor, self).ok(event=event)


class _Toolbar(aui.AuiToolBar):
    def __init__(self, parent, style):
        super(_Toolbar, self).__init__(parent, agwStyle=aui.AUI_TB_NO_AUTORESIZE)

    def AddLabelTool(self, id, label, bitmap1, bitmap2, kind, **kwargs):
        long_help_string = kwargs.pop('longHelp', '')
        short_help_string = kwargs.pop('shortHelp', '')
        bitmap2 = self.MakeDisabledBitmap(bitmap1)
        super(_Toolbar, self).AddTool(id, label, bitmap1, bitmap2, kind, 
                                      short_help_string, long_help_string, None, None)

    def GetToolState(self, toolid):
        return self.GetToolToggled(toolid)

    def SetToolBitmapSize(self, size):
        self.__size = size

    def GetToolBitmapSize(self):
        return self.__size

    def GetToolSize(self):
        return self.__size

    def SetMargins(self, *args):
        if len(args) == 2:
            super(_Toolbar, self).SetMarginsXY(args[0], args[1])
        else:
            super(_Toolbar, self).SetMargins(*args)

    def MakeDisabledBitmap(self, bitmap):
        return bitmap.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()
        
    
class ToolBar(_Toolbar, uicommand.UICommandContainerMixin):
    def __init__(self, window, settings, size=(32, 32)):
        self.__window = window
        self.__settings = settings
        self.__visibleUICommands = list()
        self.__cache = None
        super(ToolBar, self).__init__(window, style=wx.TB_FLAT|wx.TB_NODIVIDER)
        self.SetToolBitmapSize(size) 
        if operating_system.isMac():
            # Extra margin needed because the search control is too high
            self.SetMargins(0, 7)
        self.loadPerspective(window.getToolBarPerspective())

    def Clear(self):
        """The regular Clear method does not remove controls."""

        for uiCommand in self.__visibleUICommands:
            if uiCommand is not None and not isinstance(uiCommand, int):
                item = self.FindTool(uiCommand.id)
                uiCommand.unbind(self, uiCommand.id)
                if item.GetKind() == aui.ITEM_CONTROL:
                    self.DeleteTool(item.GetId())
                    item.window.Destroy()
        super(ToolBar, self).Clear()

    def getToolIdByCommand(self, commandName):
        if commandName == 'EditToolBarPerspective':
            return self.__customizeId

        for uiCommand in self.__visibleUICommands:
            if isinstance(uiCommand, uicommand.UICommand) and uiCommand.uniqueName() == commandName:
                return uiCommand.id
        return wx.ID_ANY

    def _filterCommands(self, perspective, cache=True):
        commands = list()
        if perspective:
            index = dict([(command.uniqueName(), command) for command in self.uiCommands(cache=cache) if command is not None and not isinstance(command, int)])
            index['Separator'] = None
            index['Spacer'] = 1
            for className in perspective.split(','):
                if className in index:
                    commands.append(index[className])
        else:
            commands = list(self.uiCommands(cache=cache))
        return commands

    def loadPerspective(self, perspective, customizable=True, cache=True):
        self.Clear()

        commands = self._filterCommands(perspective, cache=cache)
        self.__visibleUICommands = commands[:]

        if customizable:
            if 1 not in commands:
                commands.append(1)
            uiCommand = uicommand.EditToolBarPerspective(self, ToolBarEditor, settings=self.__settings)
            commands.append(uiCommand)
            self.__customizeId = uiCommand.id
        if operating_system.isMac():
            commands.append(None) # Errr...

        self.appendUICommands(*commands)
        self.Realize()

    def perspective(self):
        names = list()
        for uiCommand in self.__visibleUICommands:
            if uiCommand is None:
                names.append('Separator')
            elif isinstance(uiCommand, int):
                names.append('Spacer')
            else:
                names.append(uiCommand.uniqueName())
        return ','.join(names)

    def savePerspective(self, perspective):
        self.loadPerspective(perspective)
        self.__window.saveToolBarPerspective(perspective)

    def uiCommands(self, cache=True):
        if self.__cache is None or not cache:
            self.__cache = self.__window.createToolBarUICommands()
        return self.__cache

    def visibleUICommands(self):
        return self.__visibleUICommands[:]

    def AppendSeparator(self):
        ''' This little adapter is needed for 
        uicommand.UICommandContainerMixin.appendUICommands'''
        self.AddSeparator()

    def AppendStretchSpacer(self, proportion):
        self.AddStretchSpacer(proportion)

    def appendUICommand(self, uiCommand):
        return uiCommand.appendToToolBar(self)


class MainToolBar(ToolBar):
    def Realize(self):
        super(MainToolBar, self).Realize()
        wx.CallAfter(self.SetMinSize, self.GetClientSize())
