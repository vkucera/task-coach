#!/usr/bin/env python

''' ComboTreeBox provides a comboBox that pops up a tree instead of
    a list. 

    Supported platforms: wxMSW and wxMAC natively, wxGTK by means of a
                         workaround

    Author: Frank Niessink <frank@niessink.com>
    Copyright 2006, Frank Niessink
    License: wxWidgets license
    Version: 0.6
    Date: June 4, 2006
'''

import wx

__all__ = ['ComboTreeBox'] # Export only the ComboTreeBox widget


class IterableTreeCtrl(wx.TreeCtrl):
    ''' TreeCtrl is the same as wx.TreeCtrl, with a few convenience methods 
        added for easier navigation of items. '''

    def GetPreviousItem(self, item):
        ''' 
        GetPreviousItem(self, TreeItemId item) -> TreeItemId

        Returns the item that is on the line immediately above item 
        (as is displayed when the tree is fully expanded). The returned 
        item is invalid if item is the first item in the tree.
        '''
        previousSibling = self.GetPrevSibling(item)
        if previousSibling.IsOk():
            return self.GetLastChildRecursively(previousSibling)
        else:
            parent = self.GetItemParent(item)
            if parent == self.GetRootItem() and \
                (self.GetWindowStyle() & wx.TR_HIDE_ROOT):
                # Return an invalid item, because the root item is hidden
                return previousSibling
            else:
                return parent

    def GetNextItem(self, item):
        '''
        GetNextItem(self, TreeItemId item) -> TreeItemId

        Returns the item that is on the line immediately below item
        (as is displayed when the tree is fully expanded). The returned
        item is invalid if item is the last item in the tree.
        '''
        if self.ItemHasChildren(item):
            firstChild, cookie = self.GetFirstChild(item)
            return firstChild
        else:
            return self.GetNextSiblingRecursively(item)

    def GetFirstItem(self):
        '''
        GetFirstItem(self) -> TreeItemId

        Returns the very first item in the tree. This is the root item
        unless the root item is hidden. In that case the first child of
        the root item is returned, if any. If the tree is empty, an
        invalid tree item is returned.
        '''
        rootItem = self.GetRootItem()
        if rootItem.IsOk() and (self.GetWindowStyle() & wx.TR_HIDE_ROOT):
            firstChild, cookie = self.GetFirstChild(rootItem)
            return firstChild
        else:
            return rootItem

    def GetLastChildRecursively(self, item):
        '''
        GetLastChildRecursively(self, TreeItemId item) -> TreeItemId

        Returns the last child of the last child ... of item. If item
        has no children, item itself is returned. So the returned item
        is always valid, assuming a valid item has been passed. 
        '''
        lastChild = item
        while self.ItemHasChildren(lastChild):
            lastChild = self.GetLastChild(lastChild)
        return lastChild

    def GetNextSiblingRecursively(self, item):
        ''' 
        GetNextSiblingRecursively(self, TreeItemId item) -> TreeItemId

        Returns the next sibling of item if it has one. If item has no
        next sibling the next sibling of the parent of item is returned. 
        If the parent has no next sibling the next sibling of the parent 
        of the parent is returned, etc. If none of the ancestors of item
        has a next sibling, an invalid item is returned. 
        '''
        if item == self.GetRootItem():
            return wx.TreeItemId() # Return an invalid TreeItemId
        nextSibling = self.GetNextSibling(item)
        if nextSibling.IsOk():
            return nextSibling
        else:
            parent = self.GetItemParent(item)
            return self.GetNextSiblingRecursively(parent)

    def GetSelection(self):
        ''' Extend GetSelection to never return the root item if the
            root item is hidden. '''
        selection = super(IterableTreeCtrl, self).GetSelection()
        if selection == self.GetRootItem() and \
            (self.GetWindowStyle() & wx.TR_HIDE_ROOT):
            return wx.TreeItemId() # Return an invalid TreeItemId
        else:
            return selection


class BasePopupFrame(wx.MiniFrame):
    ''' BasePopupFrame is the base class for platform specific
        versions of the PopupFrame. The PopupFrame is the frame that 
        is popped up by ComboTreeBox. It contains the tree of items 
        that the user can select one item from. Upon selection, or 
        when focus is lost, the frame is hidden. '''

    def __init__(self, parent):
        super(BasePopupFrame, self).__init__(parent,
            style=wx.DEFAULT_FRAME_STYLE & wx.FRAME_FLOAT_ON_PARENT &
                  ~(wx.RESIZE_BORDER | wx.CAPTION)) 
        self._createInterior()
        self._layoutInterior()
        self._bindEventHandlers()

    def _createInterior(self):
        self._tree = IterableTreeCtrl(self, 
            style=wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT|wx.TR_HAS_BUTTONS)
        self._tree.AddRoot('Hidden root node')

    def _layoutInterior(self):
        frameSizer = wx.BoxSizer(wx.HORIZONTAL)
        frameSizer.Add(self._tree, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(frameSizer)

    def _bindEventHandlers(self):
        self._tree.Bind(wx.EVT_CHAR, self.OnChar)
        self._tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        self._tree.Bind(wx.EVT_LEFT_DOWN, self.OnMouseClick)

    def _bindKillFocus(self):
        self._tree.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

    def _unbindKillFocus(self):
        self._tree.Unbind(wx.EVT_KILL_FOCUS)

    def OnKillFocus(self, event):
        # Hide the frame so it can be popped up again later:
        self.Hide()
        self.GetParent().NotifyNoItemSelected()
        event.Skip()

    def OnChar(self, keyEvent):
        if self._keyShouldHidePopup(keyEvent):
            self.Hide()
            self.GetParent().NotifyNoItemSelected()
        keyEvent.Skip()

    def _keyShouldHidePopup(self, keyEvent):
        return keyEvent.GetKeyCode() == wx.WXK_ESCAPE

    def OnMouseClick(self, event):
        item, flags = self._tree.HitTest(event.GetPosition())
        if item.IsOk() and flags & wx.TREE_HITTEST_ONITEMLABEL:
            self._tree.SelectItem(item)
            self.Hide()
            self.GetParent().NotifyItemSelected(self._tree.GetItemText(item))
        else:
            event.Skip()

    def OnItemActivated(self, event):
        item = event.GetItem()
        self.Hide()
        self.GetParent().NotifyItemSelected(self._tree.GetItemText(item))

    def Show(self):
        self._bindKillFocus()
        wx.CallAfter(self._tree.SetFocus)
        super(BasePopupFrame, self).Show()

    def Hide(self):
        self._unbindKillFocus()
        super(BasePopupFrame, self).Hide()

    def GetTree(self):
        return self._tree


class MSWPopupFrame(BasePopupFrame):
    def Show(self):
        # Comply with the MS Windows Combobox behaviour: if the text in
        # the text field is not in the tree, the first item in the tree
        # is selected.
        if not self._tree.GetSelection().IsOk():
            self._tree.SelectItem(self._tree.GetFirstItem())
        super(MSWPopupFrame, self).Show()


class MACPopupFrame(BasePopupFrame):
    def _bindKillFocus(self):
        # On wxMac, the kill focus event doesn't work, but the
        # deactivate event does:
        self.Bind(wx.EVT_ACTIVATE, self.OnKillFocus)

    def _unbindKillFocus(self):
        self.Unbind(wx.EVT_ACTIVATE)

    def OnKillFocus(self, event):
        if not event.GetActive(): # We received a deactivate event
            self.Hide()
            wx.CallAfter(self.GetParent().NotifyNoItemSelected)
        event.Skip()


class GTKPopupFrame(BasePopupFrame):
    def _keyShouldHidePopup(self, keyEvent):
        # On wxGTK, Alt-Up also closes the popup:
        return super(GTKPopupFrame, self)._keyShouldHidePopup(keyEvent) or \
            (keyEvent.AltDown() and keyEvent.GetKeyCode() == wx.WXK_UP)


class BaseComboTreeBox(object):
    ''' BaseComboTreeBox is the base class for platform specific
        versions of the ComboTreeBox. '''

    def __init__(self, *args, **kwargs):
        style = kwargs.pop('style', 0)
        if style & wx.CB_READONLY:
            style &= ~wx.CB_READONLY # We manage readonlyness ourselves
            self._readOnly = True
        else:
            self._readOnly = False
        if style & wx.CB_SORT:
            style &= ~wx.CB_SORT # We manage sorting ourselves
            self._sort = True
        else:
            self._sort = False
        super(BaseComboTreeBox, self).__init__(style=style, *args, **kwargs)
        self._createInterior()
        self._layoutInterior()
        self._bindEventHandlers()

    # Methods to construct the widget.

    def _createInterior(self):
        self._popupFrame = self._createPopupFrame()
        self._text = self._createTextCtrl()
        self._button = self._createButton()
        self._tree = self._popupFrame.GetTree()

    def _createTextCtrl(self):
        return self # By default, the text control is the control itself.

    def _createButton(self):
        return self # By default, the dropdown button is the control itself.

    def _createPopupFrame(self):
        raise NotImplementedError # Subclass responsibility

    def _layoutInterior(self):
        pass # By default, there is no layout to be done.

    def _bindEventHandlers(self):
        for eventSource, eventType, eventHandler in self._eventsToBind():
            eventSource.Bind(eventType, eventHandler)

    def _eventsToBind(self):
        ''' _eventsToBind(self) -> 
            [(eventSource, eventType, eventHandler), ...] 
            
            _eventsToBind returns a list of eventSource, eventType,
            eventHandlers tuples that will be bound. This method can be 
            extended to bind additional events. In that case, don't 
            forget to call _eventsToBind on the super class. '''
        return [(self._text, wx.EVT_KEY_DOWN, self.OnKeyDown),
                (self._text, wx.EVT_TEXT, self.OnText),
                (self._button, wx.EVT_BUTTON, self.OnMouseClick)]

    # Event handlers

    def OnMouseClick(self, event):
        self.Popup()
        # We don't call event.Skip() to prevent popping up the
        # ComboBox's own box.

    def OnKeyDown(self, keyEvent):
        if self._keyShouldNavigate(keyEvent):
            self._navigateUpOrDown(keyEvent)
        elif self._keyShouldPopUpTree(keyEvent):
            self.Popup()
        else:
            keyEvent.Skip()

    def _keyShouldPopUpTree(self, keyEvent):
        return (keyEvent.AltDown() or keyEvent.MetaDown()) and \
                keyEvent.GetKeyCode() == wx.WXK_DOWN

    def _keyShouldNavigate(self, keyEvent):
        return keyEvent.GetKeyCode() in (wx.WXK_DOWN, wx.WXK_UP) and not \
            self._keyShouldPopUpTree(keyEvent)

    def _navigateUpOrDown(self, keyEvent):
        item = self.GetSelection()
        if item.IsOk():
            navigationMethods = {wx.WXK_DOWN: self._tree.GetNextItem, 
                                 wx.WXK_UP: self._tree.GetPreviousItem}
            getNextItem = navigationMethods[keyEvent.GetKeyCode()]
            nextItem = getNextItem(item)
        else:
            nextItem = self._tree.GetFirstItem()
        if nextItem.IsOk():
            self.SetSelection(nextItem)

    def OnText(self, event):
        event.Skip()
        item = self.FindString(self._text.GetValue())
        if item.IsOk():
            if self._tree.GetSelection() != item:
                self._tree.SelectItem(item)
        else:
            self._tree.Unselect()

    # Methods called by the PopupFrame, to let the ComboTreeBox know
    # about what the user did.

    def NotifyItemSelected(self, text):
        ''' Simulate selection of an item by the user. This is meant to 
            be called by the PopupFrame when the user selects an item. '''
        self._text.SetValue(text)
        self._postComboBoxSelectedEvent(text)
        self.SetFocus()

    def _postComboBoxSelectedEvent(self, text):
        ''' Simulate a selection event. ''' 
        event = wx.CommandEvent(wx.wxEVT_COMMAND_COMBOBOX_SELECTED, 
                                self.GetId())
        event.SetString(text)
        self.GetEventHandler().ProcessEvent(event)

    def NotifyNoItemSelected(self):
        ''' This is called by the PopupFrame when the user closes the 
            PopupFrame, without selecting an item.  '''
        self.SetFocus()

    # Misc methods, not part of the ComboBox API.

    def Popup(self):
        ''' 
        Popup(self)

        Pops up the frame with the tree.
        '''
        comboBoxSize = self.GetSize()
        x, y = self.GetParent().ClientToScreen(self.GetPosition())
        y += comboBoxSize[1]
        width = comboBoxSize[0]
        height = 300
        self._popupFrame.SetDimensions(x, y, width, height)
        # On wxGTK, when the Combobox width has been increased a call 
        # to SetMinSize is needed to force a resize of the popupFrame: 
        self._popupFrame.SetMinSize((width, height)) 
        self._popupFrame.Show()
 
    def GetTree(self):
        '''
        GetTree(self) -> wx.TreeCtrl

        Returns the tree control that is popped up. 
        '''
        return self._popupFrame.GetTree()

    # The following methods are all part of the ComboBox API (actually
    # the ControlWithItems API) and have been adapted to take TreeItemIds 
    # as parameter and return TreeItemIds, rather than indices.

    def Append(self, itemText, parent=None, clientData=None):
        ''' 
        Append(self, String itemText, TreeItemId parent=None, PyObject
               clientData=None) -> TreeItemId

        Adds the itemText to the control, associating the given clientData 
        with the item if not None. If parent is None, itemText is added
        as a root item, else itemText is added as a child item of
        parent. The return value is the TreeItemId of the newly added
        item. '''    
        if parent is None:
            parent = self._tree.GetRootItem()
        item = self._tree.AppendItem(parent, itemText, 
                                     data=wx.TreeItemData(clientData))
        if self._sort:
            self._tree.SortChildren(parent)
        return item

    def Clear(self):
        '''
        Clear(self)
        
        Removes all items from the control.
        '''
        return self._tree.DeleteAllItems()
        
    def Delete(self, item):
        '''
        Delete(self, TreeItemId item)

        Deletes the item from the control. 
        '''
        return self._tree.Delete(item)

    def FindString(self, string, parent=None):
        ''' 
        FindString(self, String string, TreeItemId parent=None) -> TreeItemId
        
        Finds the *first* item in the tree with a label equal to the
        given string. If no such item exists, an invalid item is
        returned. 
        '''
        parent = parent or self._tree.GetRootItem()
        child, cookie = self._tree.GetFirstChild(parent)
        while child.IsOk():
            if self._tree.GetItemText(child) == string:
                return child
            else:
                result = self.FindString(string, child)
                if result.IsOk():
                    return result
            child, cookie = self._tree.GetNextChild(parent, cookie)
        return child

    def GetSelection(self):
        '''
        GetSelection(self) -> TreeItemId

        Returns the TreeItemId of the selected item or an invalid item
        if no item is selected.
        '''
        selectedItem = self._tree.GetSelection()
        if selectedItem.IsOk() and selectedItem != self._tree.GetRootItem():
            return selectedItem
        else:
            return self.FindString(self.GetValue())

    def GetString(self, item):
        '''
        GetString(self, TreeItemId item) -> String

        Returns the label of the given item.
        '''
        if item.IsOk():
            return self._tree.GetItemText(item)
        else:
            return ''

    def GetStringSelection(self):
        '''
        GetStringSelection(self) -> String

        Returns the label of the selected item or an empty string if no item 
        is selected.
        '''
        return self.GetValue()

    def Insert(self, itemText, previous=None, parent=None, clientData=None):
        '''
        Insert(self, String itemText, TreeItemId previous=None, TreeItemId
               parent=None, PyObject clientData=None) -> TreeItemId

        Insert an item into the control before the ``previous`` item 
        and/or as child of the ``parent`` item. The itemText is associated 
        with clientData when not None.
        '''
        data = wx.TreeItemData(clientData)
        if parent is None:
            parent = self._tree.GetRootItem()
        if previous is None:
            item = self._tree.InsertItemBefore(parent, 0, itemText, data=data)
        else:
            item = self._tree.InsertItem(parent, previous, itemText, data=data)
        if self._sort:
            self._tree.SortChildren(parent)
        return item

    def IsEmpty(self):
        '''
        IsEmpty(self) -> bool

        Returns True if the control is empty or False if it has some items.
        '''
        return self.GetCount() == 0

    def GetCount(self):
        '''
        GetCount(self) -> int

        Returns the number of items in the control.
        '''
        # Note: We don't need to substract 1 for the hidden root item, 
        # because the TreeCtrl does that for us
        return self._tree.GetCount() 

    def SetSelection(self, item):
        ''' 
        SetSelection(self, TreeItemId item) 

        Sets the provided item to be the selected item.
        '''
        self._tree.SelectItem(item)
        self._text.SetValue(self._tree.GetItemText(item))
        
    Select = SetSelection

    def SetString(self, item, string):
        '''
        SetString(self, TreeItemId item, String string)

        Sets the label for the provided item.
        '''
        self._tree.SetItemText(item, string)
        if self._sort:
            self._tree.SortChildren(self._tree.GetItemParent(item))

    def SetStringSelection(self, string):
        '''
        SetStringSelection(self, String string) -> bool

        Selects the item with the provided string in the control. 
        Returns True if the provided string has been selected, False if
        it wasn't found in the control.
        '''
        item = self.FindString(string)
        if item.IsOk():
            if self._text.GetValue() != string:
                self._text.SetValue(string)
            self._tree.SelectItem(item)
            return True
        else:
            return False

    def GetClientData(self, item):
        '''
        GetClientData(self, TreeItemId item) -> PyObject

        Returns the client data associated with the given item, if any.
        '''
        return self._tree.GetItemPyData(item)

    def SetClientData(self, item, clientData):
        '''
        SetClientData(self, TreeItemId item, PyObject clientData)

        Associate the given client data with the provided item.
        '''
        self._tree.SetItemPyData(item, clientData)

    def GetValue(self):
        '''
        GetValue(self) -> String

        Returns the current value in the combobox text field.
        '''
        if self._text == self:
            return super(BaseComboTreeBox, self).GetValue()
        else:
            return self._text.GetValue()

    def SetValue(self, value):
        '''
        SetValue(self, String value)

        Sets the text for the combobox text field.

        NB: For a combobox with wxCB_READONLY style the string must be
        in the combobox choices list, otherwise the call to SetValue()
        is ignored.
        '''
        item = self.FindString(value)
        if self._readOnly and not item.IsOk():
            return
        if self._text == self:
            super(BaseComboTreeBox, self).SetValue(value)
        else:
            self._text.SetValue(value)
        if item.IsOk():
            if self._tree.GetSelection() != item:
                self._tree.SelectItem(item)
        else:
            self._tree.Unselect()


class NativeComboTreeBox(BaseComboTreeBox, wx.ComboBox):
    ''' NativeComboTreeBox, and any subclass, uses the native ComboBox as 
        basis, but prevent it from popping up its drop down list and
        instead pops up a PopupFrame containing a tree of items. '''

    def _eventsToBind(self):
        events = super(NativeComboTreeBox, self)._eventsToBind() 
        # Bind all mouse click events to self.OnMouseClick so we can
        # intercept those events and prevent the native Combobox from
        # popping up its list of choices.
        for eventType in (wx.EVT_LEFT_DOWN, wx.EVT_LEFT_DCLICK, 
                          wx.EVT_MIDDLE_DOWN, wx.EVT_MIDDLE_DCLICK, 
                          wx.EVT_RIGHT_DOWN, wx.EVT_RIGHT_DCLICK):
            events.append((self._button, eventType, self.OnMouseClick))
        if self._readOnly:
            events.append((self, wx.EVT_CHAR, self.OnChar))
        return events 

    def OnChar(self, event):
        # OnChar is only called when in read only mode. We don't call 
        # event.Skip() on purpose, to prevent the characters from being 
        # displayed in the text field.
        pass


class MSWComboTreeBox(NativeComboTreeBox):
    ''' MSWComboTreeBox adds one piece of functionality as compared to
        NativeComboTreeBox: when the user browses through the tree, the
        ComboTreeBox's text field is continuously updated to show the
        currently selected item in the tree. If the user cancels
        selecting a new item from the tree, e.g. by hitting escape, the
        previous value (the one that was selected before the PopupFrame
        was popped up) is restored. '''

    def _createPopupFrame(self):
        return MSWPopupFrame(self)

    def _eventsToBind(self):
        events = super(MSWComboTreeBox, self)._eventsToBind()
        events.append((self._tree, wx.EVT_TREE_SEL_CHANGED,
            self.OnSelectionChangedInTree))
        return events

    def OnSelectionChangedInTree(self, event):
        item = event.GetItem()
        if item.IsOk():
            selectedValue = self._tree.GetItemText(item)
            if self.GetValue() != selectedValue:
                self.SetValue(selectedValue)
        event.Skip()

    def _keyShouldPopUpTree(self, keyEvent):
        return super(MSWComboTreeBox, self)._keyShouldPopUpTree(keyEvent) or \
            (keyEvent.GetKeyCode() == wx.WXK_F4) or \
            ((keyEvent.AltDown() or keyEvent.MetaDown()) and \
              keyEvent.GetKeyCode() == wx.WXK_UP)

    def SetValue(self, value):
        ''' Extend SetValue to also select the text in the
            ComboTreeBox's test field. '''
        super(MSWComboTreeBox, self).SetValue(value)
        # We select the text in the ComboTreeBox's text field.
        # There is a slight complication, however. When the control is 
        # deleted, SetValue is called. But if we call SetMark at that 
        # time, wxPython will crash. We can prevent this by comparing the 
        # result of GetLastPosition and the length of the value. If they
        # match, all is fine. If they don't match, we don't call SetMark.
        if self._text.GetLastPosition() == len(value):
            self._text.SetMark(0, self._text.GetLastPosition())

    def Popup(self, *args, **kwargs):
        ''' Extend Popup to store a copy of the current value, so we can
            restore it later (in NotifyNoItemSelected). This is necessary
            because MSWComboTreeBox will change the value as the user
            browses through the items in the popped up tree. '''
        self._previousValue = self.GetValue()
        super(MSWComboTreeBox, self).Popup(*args, **kwargs)

    def NotifyNoItemSelected(self, *args, **kwargs):
        ''' Restore the value copied previously, because the user has
            not selected a new value. '''
        self.SetValue(self._previousValue)
        super(MSWComboTreeBox, self).NotifyNoItemSelected(*args, **kwargs)


class MACComboTreeBox(NativeComboTreeBox):
    def _createPopupFrame(self):
        return MACPopupFrame(self)

    def _createButton(self):
        return self.GetChildren()[0] # The choice button

    def _keyShouldNavigate(self, keyEvent):
        return False # No navigation with up and down on wxMac

    def _keyShouldPopUpTree(self, keyEvent):
        return super(MACComboTreeBox, self)._keyShouldPopUpTree(keyEvent) or \
            keyEvent.GetKeyCode() == wx.WXK_DOWN


class GTKComboTreeBox(BaseComboTreeBox, wx.Panel):
    ''' The ComboTreeBox widget for wxGTK. This is actually a work
        around because on wxGTK, there doesn't seem to be a way to intercept 
        mouse events sent to the Combobox. Intercepting those events is 
        necessary to prevent the Combobox from popping up the list and pop up
        the tree instead. So, until wxPython makes intercepting those events
        possible we build a poor man's Combobox ourselves using a TextCtrl and
        a BitmapButton.  '''

    def _createPopupFrame(self):
        return GTKPopupFrame(self)

    def _createTextCtrl(self):
        if self._readOnly:
            style = wx.TE_READONLY
        else:
            style = 0
        return wx.TextCtrl(self, style=style)

    def _createButton(self):
        bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, client=wx.ART_BUTTON)
        return wx.BitmapButton(self, bitmap=bitmap)

    def _layoutInterior(self):
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        panelSizer.Add(self._text, flag=wx.EXPAND, proportion=1)
        panelSizer.Add(self._button)
        self.SetSizerAndFit(panelSizer)


def ComboTreeBox(*args, **kwargs):
    ''' Factory function to create the right ComboTreeBox depending on
        platform. You may force a specific class by setting the keyword
        argument 'platform', e.g. 'platform=GTK' or 'platform=MSW' or 
        platform='MAC'. '''

    platform = kwargs.pop('platform', None) or wx.PlatformInfo[0][4:7]
    ComboTreeBoxClassName = '%sComboTreeBox' % platform
    ComboTreeBoxClass = globals()[ComboTreeBoxClassName]
    return ComboTreeBoxClass(*args, **kwargs)


# Demo

class DemoFrame(wx.Frame):
    def __init__(self, platform):
        super(DemoFrame, self).__init__(None, title='ComboTreeBox Demo')
        panel = wx.Panel(self)
        panelSizer = wx.FlexGridSizer(2, 2)
        panelSizer.AddGrowableCol(1)
        for style, labelText in [(0, 'Default style:'), 
                                 (wx.CB_READONLY, 'Read-only style:')]:
            label = wx.StaticText(panel, label=labelText)
            panelSizer.Add(label, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, 
                           border=5)
            comboBox = self._createComboTreeBox(panel, style, platform)
            panelSizer.Add(comboBox, flag=wx.EXPAND|wx.ALL, border=5)
        panel.SetSizerAndFit(panelSizer)
        self.Fit()

    def _createComboTreeBox(self, parent, style, platform):
        comboBox = ComboTreeBox(parent, style=style, platform=platform)
        self._bindEventHandlers(comboBox)
        for i in range(5):
            child = comboBox.Append('Item %d'%i)
            for j in range(5):
                grandChild = comboBox.Append('Item %d.%d'%(i,j), child)
                for k in range(5):
                    comboBox.Append('Item %d.%d.%d'%(i,j, k), grandChild)
        return comboBox
        
    def _bindEventHandlers(self, comboBox):
        for eventType, handler in [(wx.EVT_COMBOBOX, self.onItemSelected), 
                                   (wx.EVT_TEXT, self.onItemEntered)]:
            comboBox.Bind(eventType, handler)

    def onItemSelected(self, event):
        print 'You selected: %s'%event.GetString()
        event.Skip()

    def onItemEntered(self, event):
        print 'You entered: %s'%event.GetString()
        event.Skip()


# Unittests

import unittest

class ComboTreeBoxTest(unittest.TestCase):
    def setUp(self):
        self.comboBoxEventReceived = False
        frame = wx.Frame(None)
        self.comboBox = ComboTreeBox(frame, platform=platform)
        self.tree = self.comboBox._popupFrame.GetTree()

    def onComboBox(self, event):
        self.comboBoxEventReceived = True

    def testComboBoxIsEmptyByDefault(self):
        self.assertEqual(0, self.comboBox.GetCount())

    def testAddingOneItem(self):
        self.comboBox.Append('Item 1')
        self.assertEqual(1, self.comboBox.GetCount())

    def testAddingTwoItems(self):
        self.comboBox.Append('Item 1')
        self.comboBox.Append('Item 2')
        self.assertEqual(2, self.comboBox.GetCount())

    def testAddingTwoParentAndChild(self):
        item1 = self.comboBox.Append('Item 1')
        self.comboBox.Append('Item 2', item1)
        self.assertEqual(2, self.comboBox.GetCount())

    def testSelectingAnItemPutsItInTheComboBox(self):
        self.comboBox.Append('Item 1')
        self.comboBox.Bind(wx.EVT_COMBOBOX, self.onComboBox)
        self.comboBox.NotifyItemSelected('Item 1')
        self.failUnless(self.comboBoxEventReceived)

    def testClear(self):
        self.comboBox.Append('Item 1')
        self.comboBox.Clear()
        self.assertEqual(0, self.comboBox.GetCount())

    def testDelete(self):
        self.comboBox.Append('Item 1')
        self.comboBox.Delete(self.tree.GetFirstItem())
        self.assertEqual(0, self.comboBox.GetCount())

    def testGetSelection_NoItems(self):
        self.failIf(self.comboBox.GetSelection().IsOk())

    def testGetSelection_NoSelection(self):
        self.comboBox.Append('Item 1')
        self.failIf(self.comboBox.GetSelection().IsOk())

    def testGetSelection_WithSelection(self):
        item1 = self.comboBox.Append('Item 1')
        self.comboBox.SetValue('Item 1')
        self.assertEqual(item1, self.comboBox.GetSelection())

    def testGetSelection_EquallyNamedNodes_SelectedInTree(self):
        item1 = self.comboBox.Append('Item')
        item2 = self.comboBox.Append('Item')
        self.tree.SelectItem(item2)
        self.assertEqual(self.tree.GetSelection(), self.comboBox.GetSelection())

    def testGetSelection_EquallyNamedNodes_TypedInTextBox(self):
        item1 = self.comboBox.Append('Item')
        item2 = self.comboBox.Append('Item')
        self.comboBox.SetValue('Item')
        self.assertEqual(item1, self.comboBox.GetSelection())

    def testFindString_NotPresent(self):
        self.comboBox.Append('Item 1')
        self.failIf(self.comboBox.FindString('Item 2').IsOk())

    def testFindString_Present(self):
        self.comboBox.Append('Item 1')
        self.assertEqual(self.tree.GetFirstItem(),
                         self.comboBox.FindString('Item 1'))

    def testFindString_Child(self):
        parent = self.comboBox.Append('Parent')
        child = self.comboBox.Append('Child', parent=parent)
        self.assertEqual(child, self.comboBox.FindString('Child'))

    def testGetString_NotPresent(self):
        self.assertEqual('', self.comboBox.GetString(self.tree.GetFirstItem()))

    def testGetString_Present(self):
        self.comboBox.Append('Item 1')
        self.assertEqual('Item 1', 
            self.comboBox.GetString(self.tree.GetFirstItem()))

    def testGetStringSelection_NotPresent(self):
        self.assertEqual('', self.comboBox.GetStringSelection())

    def testGetStringSelection_Present(self):
        self.comboBox.SetValue('Item 1')
        self.assertEqual('Item 1', self.comboBox.GetStringSelection())

    def testInsertAsFirstItem(self):
        self.comboBox.Insert('Item 1')
        self.assertEqual('Item 1', 
            self.comboBox.GetString(self.tree.GetFirstItem()))

    def testInsertAsFirstItemBeforeExistingItem(self):
        item1 = self.comboBox.Append('Item 1')
        item2 = self.comboBox.Insert('Item 2')
        self.assertEqual(item2, self.tree.GetFirstItem())

    def testInsertAsFirstChildBeforeExistingChild(self):
        parent = self.comboBox.Append('parent')
        child1 = self.comboBox.Append('child 1', parent)
        child2 = self.comboBox.Insert('child 2', parent=parent)
        self.assertEqual(child2, self.tree.GetFirstChild(parent)[0])

    def testSelect(self):
        item1 = self.comboBox.Append('Item 1')
        self.comboBox.Select(item1)
        self.assertEqual('Item 1', self.comboBox.GetValue())

    def testSetString(self):
        item1 = self.comboBox.Append('Item 1')
        self.comboBox.SetString(item1, 'Item 2')
        self.assertEqual('Item 2', self.comboBox.GetString(item1))

    def testSetStringSelection_ExistingString(self):
        self.comboBox.Append('Hi')
        self.comboBox.SetStringSelection('Hi')
        self.assertEqual('Hi', self.comboBox.GetStringSelection())

    def testSetStringSelection_NonExistingString(self):
        self.comboBox.SetStringSelection('Hi')
        self.assertEqual('', self.comboBox.GetStringSelection())

    def testAppendWithClientData(self):
        item1 = self.comboBox.Append('Item 1', clientData=[1,2,3])
        self.assertEqual([1,2,3], self.comboBox.GetClientData(item1))

    def testInsertWithClientData(self):
        item1 = self.comboBox.Append('Item 1')
        item2 = self.comboBox.Insert('Item 2', previous=item1, 
                                     clientData=[1,2,3])
        self.assertEqual([1,2,3], self.comboBox.GetClientData(item2))

    def testSetClientData(self):
        item1 = self.comboBox.Append('Item 1')
        self.comboBox.SetClientData(item1, [1,2,3])
        self.assertEqual([1,2,3], self.comboBox.GetClientData(item1))


class SortedComboTreeBoxTest(unittest.TestCase):
    def setUp(self):
        frame = wx.Frame(None)
        self.comboBox = ComboTreeBox(frame, style=wx.CB_SORT, platform=platform)
        self.tree = self.comboBox._popupFrame.GetTree()

    def testAppend(self):
        itemB = self.comboBox.Append('B')
        itemA = self.comboBox.Append('A')
        self.assertEqual(itemA, self.tree.GetFirstItem())

    def testInsert(self):
        itemA = self.comboBox.Append('A')
        itemB = self.comboBox.Insert('B')
        self.assertEqual(itemA, self.tree.GetFirstItem())

    def testAppend_Child(self):
        itemA = self.comboBox.Append('A')
        itemA2 = self.comboBox.Append('2', parent=itemA)
        itemA1 = self.comboBox.Append('1', parent=itemA)
        self.assertEqual(itemA1, self.tree.GetFirstChild(itemA)[0])

    def testInsert_Child(self):
        itemA = self.comboBox.Append('A')
        itemA1 = self.comboBox.Append('1', parent=itemA)
        itemA2 = self.comboBox.Insert('2', parent=itemA)
        self.assertEqual(itemA1, self.tree.GetFirstChild(itemA)[0])
        
    def testSetString(self):
        itemB = self.comboBox.Append('B')
        itemC = self.comboBox.Append('C')
        self.comboBox.SetString(itemC, 'A')
        self.assertEqual(itemC, self.tree.GetFirstItem())


class ReadOnlyComboTreeBoxTest(unittest.TestCase):
    def setUp(self):
        frame = wx.Frame(None)
        self.comboBox = ComboTreeBox(frame, style=wx.CB_READONLY)
        self.tree = self.comboBox._popupFrame.GetTree()

    def testSetValue_ToNonExistingValue(self):
        self.comboBox.SetValue('Ignored value')
        self.assertEqual('', self.comboBox.GetValue())

    def testSetValue_ToExistingValue(self):
        self.comboBox.Append('This works')
        self.comboBox.SetValue('This works')
        self.assertEqual('This works', self.comboBox.GetValue())


class IterableTreeCtrlTest(unittest.TestCase):
    def setUp(self):
        self.frame = wx.Frame(None)
        self.tree = IterableTreeCtrl(self.frame)
        self.root = self.tree.AddRoot('root')

    def testPreviousOfRootIsInvalid(self):
        item = self.tree.GetPreviousItem(self.root)
        self.failIf(item.IsOk())

    def testPreviousOfChildOfRootIsRoot(self):
        child = self.tree.AppendItem(self.root, 'child')
        self.assertEqual(self.root, self.tree.GetPreviousItem(child))

    def testPreviousOfSecondChildOfRootIsFirstChild(self):
        child1 = self.tree.AppendItem(self.root, 'child1')
        child2 = self.tree.AppendItem(self.root, 'child2')
        self.assertEqual(child1, self.tree.GetPreviousItem(child2))

    def testPreviousOfGrandChildIsChild(self):
        child = self.tree.AppendItem(self.root, 'child')
        grandchild = self.tree.AppendItem(child, 'grandchild')
        self.assertEqual(child, self.tree.GetPreviousItem(grandchild))

    def testPreviousOfSecondChildWhenFirstChildHasChildIsThatChild(self):
        child1 = self.tree.AppendItem(self.root, 'child1')
        grandchild = self.tree.AppendItem(child1, 'child of child1')
        child2 = self.tree.AppendItem(self.root, 'child2')
        self.assertEqual(grandchild, self.tree.GetPreviousItem(child2))

    def testPreviousOfSecondChildWhenFirstChildHasGrandChildIsThatGrandChild(self):
        child1 = self.tree.AppendItem(self.root, 'child1')
        grandchild = self.tree.AppendItem(child1, 'child of child1')
        greatgrandchild = self.tree.AppendItem(grandchild, 
            'grandchild of child1')
        child2 = self.tree.AppendItem(self.root, 'child2')
        self.assertEqual(greatgrandchild, self.tree.GetPreviousItem(child2))

    def testNextOfRootIsInvalidWhenRootHasNoChildren(self):
        item = self.tree.GetNextItem(self.root)
        self.failIf(item.IsOk())

    def testNextOfRootIsItsChildWhenRootHasOneChild(self):
        child = self.tree.AppendItem(self.root, 'child')
        self.assertEqual(child, self.tree.GetNextItem(self.root))

    def testNextOfLastChildIsInvalid(self):
        child = self.tree.AppendItem(self.root, 'child')
        self.failIf(self.tree.GetNextItem(child).IsOk())

    def testNextOfFirstChildIsSecondChild(self):
        child1 = self.tree.AppendItem(self.root, 'child1')
        child2 = self.tree.AppendItem(self.root, 'child2')
        self.assertEqual(child2, self.tree.GetNextItem(child1))

    def testNextOfGrandChildIsItsParentsSibling(self):
        child1 = self.tree.AppendItem(self.root, 'child1')
        grandchild = self.tree.AppendItem(child1, 'child of child1')
        child2 = self.tree.AppendItem(self.root, 'child2')
        self.assertEqual(child2, self.tree.GetNextItem(grandchild))

    def testNextOfGreatGrandChildIsItsParentsSiblingRecursively(self):
        child1 = self.tree.AppendItem(self.root, 'child1')
        grandchild = self.tree.AppendItem(child1, 'child of child1')
        greatgrandchild = self.tree.AppendItem(grandchild, 
            'grandchild of child1')
        child2 = self.tree.AppendItem(self.root, 'child2')
        self.assertEqual(child2, self.tree.GetNextItem(greatgrandchild))

    def testNextOfGrandChildWhenItIsLastIsInvalid(self):
        child = self.tree.AppendItem(self.root, 'child')
        grandchild = self.tree.AppendItem(child, 'child of child')
        self.failIf(self.tree.GetNextItem(grandchild).IsOk())

    def testFirstItemIsRoot(self):
        self.assertEqual(self.root, self.tree.GetFirstItem())

    def testGetFirstItemWithoutRootIsInvalid(self):
        tree = IterableTreeCtrl(self.frame)
        self.failIf(tree.GetFirstItem().IsOk())

    def testGetSelection_NoSelection(self):
        self.tree.Unselect()
        self.failIf(self.tree.GetSelection().IsOk())

    def testGetSelection_RootItemSelected(self):
        self.tree.SelectItem(self.tree.GetRootItem())
        self.assertEqual(self.tree.GetRootItem(), self.tree.GetSelection())

    def testGetSelection_OtherItem(self):
        child = self.tree.AppendItem(self.root, 'child')
        self.tree.SelectItem(child)
        self.assertEqual(child, self.tree.GetSelection())


class IterableTreeCtrlWithHiddenRootTest(unittest.TestCase):
    def setUp(self):
        frame = wx.Frame(None)
        self.tree = IterableTreeCtrl(frame, style=wx.TR_HIDE_ROOT)
        self.root = self.tree.AddRoot('root')

    def testPreviousOfChildOfRootIsInvalid(self):
        child = self.tree.AppendItem(self.root, 'child')
        self.failIf(self.tree.GetPreviousItem(child).IsOk())

    def testNextOfGrandChildWhenItIsLastIsInvalid(self):
        child = self.tree.AppendItem(self.root, 'child')
        grandchild = self.tree.AppendItem(child, 'child of child')
        self.failIf(self.tree.GetNextItem(grandchild).IsOk())

    def testRootIsNotTheFirstItem(self):
        self.failIf(self.tree.GetFirstItem().IsOk())

    def testFirstChildOfRootIsTheFirstItem(self):
        child = self.tree.AppendItem(self.root, 'child')
        self.assertEqual(child, self.tree.GetFirstItem())

    def testGetSelection_NoSelection(self):
        self.tree.Unselect()
        self.failIf(self.tree.GetSelection().IsOk())

    def testGetSelection_RootItemSelected(self):
        # Apparently, selecting a hidden root item crashes wxPython on
        # Windows, so don't do that.
        if '__WXMSW__' not in wx.PlatformInfo:
            self.tree.SelectItem(self.tree.GetRootItem())
            self.failIf(self.tree.GetSelection().IsOk())

    def testGetSelection_OtherItem(self):
        child = self.tree.AppendItem(self.root, 'child')
        self.tree.SelectItem(child)
        self.assertEqual(child, self.tree.GetSelection())

     

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] not in
        ['demo', 'test']):
        print "Usage: %s 'demo' | 'test' ['MSW' | 'MAC' | 'GTK']"%sys.argv[0]
        sys.exit(1)
    if len(sys.argv) > 2:
        platform = sys.argv[2].upper()
        del sys.argv[2]
    else:
        platform = None

    app = wx.App(False)
    if sys.argv[1] == 'test':
        # Remove the 'test' command line argument otherwise unittest.main 
        # will try to use it to load tests.
        del sys.argv[1] 
        unittest.main()
    elif sys.argv[1] == 'demo':
        frame = DemoFrame(platform)
        frame.Show()
        app.MainLoop()

