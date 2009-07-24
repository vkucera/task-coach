"""
treemixin.py - module based on the treemixin in wxPython, but stripped to
contain what is needed for Task Coach. Goal is to phase it out completely.

"""

import wx


class TreeAPIHarmonizer(object):
    """ This class attempts to hide the differences in API between the
    different tree controls that are part of wxPython. """

    def __callSuper(self, methodName, default, *args, **kwargs):
        # If our super class has a method called methodName, call it,
        # otherwise return the default value.
        superClass = super(TreeAPIHarmonizer, self)
        if hasattr(superClass, methodName):
            return getattr(superClass, methodName)(*args, **kwargs)
        else:
            return default
        
    def SetItemType(self, item, newType):
        # CustomTreeCtrl doesn't support changing the item type on the fly,
        # so we create a new item and delete the old one. We currently only
        # keep the item text, would be nicer to also retain other attributes.
        text = self.GetItemText(item)
        newItem = self.InsertItem(self.GetItemParent(item), item, text, 
                                  ct_type=newType)
        self.Delete(item)
        return newItem

    def GetMainWindow(self, *args, **kwargs):
        # Only TreeListCtrl has a separate main window, return self if we are 
        # mixed in with another tree control.
        return self.__callSuper('GetMainWindow', self, *args, **kwargs)
    
    MainWindow = property(fget=GetMainWindow)

    def GetItemImage(self, item, which=wx.TreeItemIcon_Normal, column=0):
        # CustomTreeCtrl always wants the which argument, so provide it.
        # TreeListCtrl.GetItemImage has a different order of arguments than
        # the other tree controls. Hide the differences.
        if self.GetColumnCount():
            if column < 0:
                column = 0
            args = (item, column, which)
        else:
            args = (item, which)
        return super(TreeAPIHarmonizer, self).GetItemImage(*args)

    def SetItemImage(self, item, imageIndex, which=wx.TreeItemIcon_Normal, 
                     column=0):
        # The SetItemImage signature is different for TreeListCtrl and
        # other tree controls. This adapter method hides the differences.
        if self.GetColumnCount():
            if column < 0:
                column = 0
            args = (item, imageIndex, column, which)
        else:
            args = (item, imageIndex, which)
        super(TreeAPIHarmonizer, self).SetItemImage(*args)

    def UnselectAll(self):
        # Unselect all items, regardless of whether we are in multiple 
        # selection mode or not.
        if self.HasFlag(wx.TR_MULTIPLE):
            super(TreeAPIHarmonizer, self).UnselectAll()
        else:
            # CustomTreeCtrl Unselect() doesn't seem to work in all cases,
            # also invoke UnselectAll just to be sure.
            self.Unselect()
            super(TreeAPIHarmonizer, self).UnselectAll()

    def GetCount(self):
        # TreeListCtrl correctly ignores the root item when it is hidden,
        # but doesn't count the root item when it is visible
        itemCount = super(TreeAPIHarmonizer, self).GetCount()
        if self.GetColumnCount() and not self.HasFlag(wx.TR_HIDE_ROOT):
            itemCount += 1
        return itemCount

    def GetSelections(self):
        # Always return a list of selected items, regardless of whether
        # we are in multiple selection mode or not.
        if self.HasFlag(wx.TR_MULTIPLE):
            selections = super(TreeAPIHarmonizer, self).GetSelections()
        else:
            selection = self.GetSelection()
            if selection:
                selections = [selection]
            else:
                selections = []
        # If the root item is hidden, it should never be selected, 
        # unfortunately, CustomTreeCtrl allows it to be selected.
        if self.HasFlag(wx.TR_HIDE_ROOT):
            rootItem = self.GetRootItem()
            if rootItem and rootItem in selections:
                selections.remove(rootItem)
        return selections

    def GetFirstVisibleItem(self):
        # TreeListCtrl raises an exception or even crashes when invoking 
        # GetFirstVisibleItem on an empty tree, so don't do that.
        rootItem = self.GetRootItem()
        if rootItem:
            # wxPython 2.8.6.1 on Linux returns the hidden root item as first 
            # visible item, fix that if necessary
            firstVisibleItem = super(TreeAPIHarmonizer, 
                                     self).GetFirstVisibleItem()
            if self.HasFlag(wx.TR_HIDE_ROOT) and firstVisibleItem == rootItem:
                return self.GetNextVisible(firstVisibleItem)
            else:
                return firstVisibleItem
        else:
            return wx.TreeItemId()

    def SelectItem(self, item, *args, **kwargs):
        # Prevent the hidden root from being selected, otherwise TreeCtrl
        # crashes 
        if self.HasFlag(wx.TR_HIDE_ROOT) and item == self.GetRootItem():
            return
        else:
            return super(TreeAPIHarmonizer, self).SelectItem(item, *args, 
                                                             **kwargs)
        
    def HitTest(self, point, *args, **kwargs):
        """ HitTest returns a two-tuple (item, flags) for tree controls
        without columns and a three-tuple (item, flags, column) for tree
        controls with columns. Our caller can indicate this method to
        always return a three-tuple no matter what tree control we're mixed
        in with by specifying the optional argument 'alwaysReturnColumn'
        to be True. In addition, CustomTreeCtrl.HitTest is inconsistent with
        the other tree controls. It wants the point to be a wx.Point, so if 
        the user supplied a (x, y) tuple, translate it first. Also, when no 
        item is found under point, CustomTreeCtrl returns None as item. 
        For consistency, we convert None to an invalid item before returning 
        it. """
        alwaysReturnColumn = kwargs.pop('alwaysReturnColumn', False)
        if type(point) == type(()):
            point = wx.Point(point[0], point[1])
        hitTestResult = super(TreeAPIHarmonizer, self).HitTest(point, *args, 
                                                               **kwargs)
        if len(hitTestResult) == 2 and alwaysReturnColumn:
            hitTestResult += (0,)
        if hitTestResult[0] is None:
            hitTestResult = (wx.TreeItemId(),) + hitTestResult[1:]
        return hitTestResult
        

class TreeHelper(object):
    """ This class provides methods that are not part of the API of any 
    tree control, but are convenient to have available. """

    def GetItemChildren(self, item=None, recursively=False):
        """ Return the children of item as a list. """
        if not item:
            item = self.GetRootItem()
            if not item:
                return []
        children = []
        child, cookie = self.GetFirstChild(item)
        while child:
            children.append(child)
            if recursively:
                children.extend(self.GetItemChildren(child, True))
            child, cookie = self.GetNextChild(item, cookie)
        return children

    def GetIndexOfItem(self, item):
        """ Return the index of item. """
        parent = self.GetItemParent(item)
        if parent:
            parentIndices = self.GetIndexOfItem(parent)
            ownIndex = self.GetItemChildren(parent).index(item) # FIXME: Can raise ValueError: list.index(x): x not in list
            return parentIndices + (ownIndex,)
        else:
            return ()

    def GetItemByIndex(self, index):
        """ Return the item specified by index. """
        item = self.GetRootItem()
        for i in index:
            children = self.GetItemChildren(item)
            item = children[i]
        return item


class VirtualTree(TreeAPIHarmonizer, TreeHelper):
    """ This is a mixin class that can be used to allow for virtual tree
    controls. It can be mixed in with wx.TreeCtrl, wx.gizmos.TreeListCtrl, 
    wx.lib.customtree.CustomTreeCtrl.

    To use it derive a new class from this class and one of the tree
    controls, e.g.:
    class MyTree(VirtualTree, wx.TreeCtrl):
        ...

    VirtualTree uses several callbacks (such as OnGetItemText) to 
    retrieve information needed to construct the tree and render the 
    items. To specify what item the callback needs information about,
    the callback passes an item index. Whereas for list controls a simple
    integer index can be used, for tree controls indicating a specific
    item is a little bit more complicated. See below for a more detailed 
    explanation of how indices work.

    Note that VirtualTree forces the wx.TR_HIDE_ROOT style.

    In your subclass you *must* override OnGetItemText and 
    OnGetChildrenCount. These two methods are the minimum needed to 
    construct the tree and render the item labels. If you want to add 
    images, change fonts our colours, etc., you need to override the 
    appropriate OnGetXXX method as well.

    About indices: your callbacks are passed a tuple of integers that 
    identifies the item the VirtualTree wants information about. An 
    empty tuple, i.e. (), represents the hidden root item.  A tuple with 
    one integer, e.g. (3,), represents a visible root item, in this case 
    the fourth one. A tuple with two integers, e.g. (3,0), represents a 
    child of a visible root item, in this case the first child of the 
    fourth root item. 
    """

    def __init__(self, *args, **kwargs):
        kwargs['style'] = kwargs.get('style', wx.TR_DEFAULT_STYLE) | \
                          wx.TR_HIDE_ROOT
        super(VirtualTree, self).__init__(*args, **kwargs)

    def OnGetChildrenCount(self, index):
        """ This function *must* be overloaded in the derived class.
        It should return the number of child items of the item with the 
        provided index. If index == () it should return the number of 
        root items. """
        raise NotImplementedError

    def OnGetItemText(self, index, column=0):
        """ This function *must* be overloaded in the derived class. It 
        should return the string containing the text of the specified
        item. """
        raise NotImplementedError
    
    def OnGetItemExpanded(self, index):
        """ This function may be overloaded in the derived class. It
        should return whether this item is expanded (True) or not (False). """
        return 'Undetermined'

    def OnGetItemFont(self, index):
        """ This function may be overloaded in the derived class. It 
        should return the wx.Font to be used for the specified item. """
        return wx.NullFont 

    def OnGetItemTextColour(self, index):
        """ This function may be overloaded in the derived class. It 
        should return the wx.Colour to be used as text colour for the 
        specified item. """
        return wx.NullColour

    def OnGetItemBackgroundColour(self, index):
        """ This function may be overloaded in the derived class. It 
        should return the wx.Colour to be used as background colour for 
        the specified item. """
        return wx.NullColour

    def OnGetItemImage(self, index, which=wx.TreeItemIcon_Normal, column=0):
        """ This function may be overloaded in the derived class. It 
        should return the index of the image to be used. Don't forget
        to associate an ImageList with the tree control. """
        return -1

    def OnGetItemType(self, index):
        """ This function may be overloaded in the derived class, but
        that only makes sense when this class is mixed in with a tree 
        control that supports checkable items, i.e. CustomTreeCtrl. 
        This method should return whether the item is to be normal (0,
        the default), a checkbox (1) or a radiobutton (2). 
        Note that OnGetItemChecked needs to be implemented as well; it
        should return whether the item is actually checked. """
        return 0 

    def OnGetItemChecked(self, index):
        """ This function may be overloaded in the derived class, but
        that only makes sense when this class is mixed in with a tree 
        control that supports checkable items, i.e. CustomTreeCtrl. 
        This method should return whether the item is to be checked. 
        Note that OnGetItemType should return 1 (checkbox) or 2
        (radiobutton) for this item. """
        return False 

    def RefreshItems(self):
        """ Redraws all items. """
        rootItem = self.GetRootItem()
        if not rootItem:
            rootItem = self.AddRoot('Hidden root')
        self.RefreshChildrenRecursively(rootItem)
        self.Update()
        # Expanding and collapsing trigger events, and the event handlers
        # might query the tree before we're done refreshing, so postpone
        # expanding and collapsing items until we're done refreshing.
        self.RefreshExpansionStatesRecursively(rootItem)
        
    def RefreshItem(self, index):
        """ Redraws the item with the specified index. """
        try:
            item = self.GetItemByIndex(index)
        except IndexError:
            # There's no corresponding item for index, because its parent
            # has not been expanded yet.
            return
        hasChildren = bool(self.OnGetChildrenCount(index))
        self.DoRefreshItem(item, index, hasChildren)

    def RefreshChildrenRecursively(self, item, itemIndex=None):
        """ Refresh the children of item, reusing as much of the
        existing items in the tree as possible. """
        if itemIndex is None:
            itemIndex = self.GetIndexOfItem(item)
        reusableChildren = self.GetItemChildren(item)
        for childIndex in self.ChildIndices(itemIndex):
            if reusableChildren: 
                child = reusableChildren.pop(0) 
            else:
                child = self.AppendItem(item, '')
            self.RefreshItemRecursively(child, childIndex)
        for unusedChild in reusableChildren:
            self.Delete(unusedChild)
                          
    def RefreshItemRecursively(self, item, itemIndex):
        """ Refresh the item and its children recursively. """
        hasChildren = bool(self.OnGetChildrenCount(itemIndex))
        item = self.DoRefreshItem(item, itemIndex, hasChildren)
        if hasChildren:
            self.RefreshChildrenRecursively(item, itemIndex)
        else:
            self.DeleteChildren(item)
 
    def DoRefreshItem(self, item, index, hasChildren):
        """ Refresh one item. """
        item = self.RefreshItemType(item, index)
        self.RefreshItemText(item, index)
        self.RefreshColumns(item, index)
        self.RefreshItemFont(item, index)
        self.RefreshTextColour(item, index)
        self.RefreshBackgroundColour(item, index)
        self.RefreshItemImage(item, index, hasChildren)
        self.RefreshCheckedState(item, index)
        return item
        
    def RefreshItemType(self, item, index):
        return self.__refreshAttribute(item, index, 'ItemType')
        
    def RefreshItemText(self, item, index):
        self.__refreshAttribute(item, index, 'ItemText')

    def RefreshColumns(self, item, index):
        for columnIndex in range(1, self.GetColumnCount()):
            self.__refreshAttribute(item, index, 'ItemText', columnIndex)

    def RefreshItemFont(self, item, index):
        value = self.OnGetItemFont(index)
        if value == wx.NullFont:
            return
        self.__refreshAttribute(item, index, 'ItemFont')

    def RefreshTextColour(self, item, index):
        self.__refreshAttribute(item, index, 'ItemTextColour')

    def RefreshBackgroundColour(self, item, index):
        self.__refreshAttribute(item, index, 'ItemBackgroundColour')

    regularIcons = [wx.TreeItemIcon_Normal, wx.TreeItemIcon_Selected]
    expandedIcons = [wx.TreeItemIcon_Expanded, 
                     wx.TreeItemIcon_SelectedExpanded]

    def RefreshItemImage(self, item, index, hasChildren):
        # Refresh images in first column:
        for icon in self.regularIcons:
            self.__refreshAttribute(item, index, 'ItemImage', icon)
        for icon in self.expandedIcons:
            if hasChildren:
                imageIndex = self.OnGetItemImage(index, icon)
            else:
                imageIndex = -1
            if self.GetItemImage(item, icon) != imageIndex or imageIndex == -1:
                self.SetItemImage(item, imageIndex, icon)
        # Refresh images in remaining columns, if any:
        for columnIndex in range(1, self.GetColumnCount()):
            for icon in self.regularIcons:
                self.__refreshAttribute(item, index, 'ItemImage', icon, 
                                        columnIndex)

    def RefreshCheckedState(self, item, index):
        self.__refreshAttribute(item, index, 'ItemChecked')

    def RefreshExpansionStatesRecursively(self, item):
        for child in self.GetItemChildren(item, recursively=True):
            self.RefreshExpansionState(child, self.GetIndexOfItem(child))

    def RefreshExpansionState(self, item, itemIndex):
        itemShouldBeExpanded = self.OnGetItemExpanded(itemIndex)
        if itemShouldBeExpanded == 'Undetermined':
            return
        itemIsExpanded = self.IsExpanded(item)
        if itemShouldBeExpanded and not itemIsExpanded:
            self.Expand(item)
        elif not itemShouldBeExpanded and itemIsExpanded:
            self.Collapse(item)        
        
    def ChildIndices(self, itemIndex):
        childrenCount = self.OnGetChildrenCount(itemIndex) 
        return [itemIndex + (childNumber,) for childNumber \
                in range(childrenCount)]

    def __refreshAttribute(self, item, index, attribute, *args):
        """ Refresh the specified attribute if necessary. """
        value = getattr(self, 'OnGet%s'%attribute)(index, *args)
        if self.__getAttribute(attribute)(item, *args) != value:
            return self.__setAttribute(attribute)(item, value, *args)
        else:
            return item
        
    def __getAttribute(self, attribute):
        try:
            return getattr(self, 'Get%s'%attribute)
        except AttributeError:
            return getattr(self, 'Is%s'%attribute)

    def __setAttribute(self, attribute):
        try:
            return getattr(self, 'Set%s'%attribute)
        except AttributeError:
            if attribute == 'ItemChecked':
                return getattr(self, 'CheckItem')
            else:
                raise


class DragAndDrop(TreeAPIHarmonizer, TreeHelper):
    """ This is a mixin class that can be used to easily implement
    dragging and dropping of tree items. It can be mixed in with 
    wx.TreeCtrl, wx.gizmos.TreeListCtrl, or wx.lib.customtree.CustomTreeCtrl.

    To use it derive a new class from this class and one of the tree
    controls, e.g.:
    class MyTree(DragAndDrop, wx.TreeCtrl):
        ...

    You *must* implement OnDrop. OnDrop is called when the user has
    dropped an item on top of another item. It's up to you to decide how
    to handle the drop. If you are using this mixin together with the
    VirtualTree mixin, it makes sense to rearrange your underlying data
    and then call RefreshItems to let the virtual tree refresh itself. """    
 
    def __init__(self, *args, **kwargs):
        kwargs['style'] = kwargs.get('style', wx.TR_DEFAULT_STYLE) | \
                          wx.TR_HIDE_ROOT
        super(DragAndDrop, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)

    def OnDrop(self, dropItem, dragItem):
        """ This function must be overloaded in the derived class.
        dragItem is the item being dragged by the user. dropItem is the
        item dragItem is dropped upon. If the user doesn't drop dragItem
        on another item, dropItem equals the (hidden) root item of the
        tree control. """
        raise NotImplementedError

    def OnBeginDrag(self, event):
        # We allow only one item to be dragged at a time, to keep it simple
        if self.GetSelections():
            self._dragItem = self.GetSelections()[0]
        else:
            self._dragItem = event.GetItem()
        if self._dragItem and self._dragItem != self.GetRootItem(): 
            self.StartDragging()
            event.Allow()
        else:
            event.Veto()

    def OnEndDrag(self, event):
        self.StopDragging()
        dropTarget = event.GetItem()
        if not dropTarget:
            dropTarget = self.GetRootItem()
        if self.IsValidDropTarget(dropTarget):
            self.UnselectAll()
            if dropTarget != self.GetRootItem():
                self.SelectItem(dropTarget)
            self.OnDrop(dropTarget, self._dragItem)
        
    def OnDragging(self, event):
        if not event.Dragging():
            self.StopDragging()
            return
        item, flags, column = self.HitTest(wx.Point(event.GetX(), event.GetY()),
                                           alwaysReturnColumn=True)
        if not item:
            item = self.GetRootItem()
        if self.IsValidDropTarget(item):
            self.SetCursorToDragging()
        else:
            self.SetCursorToDroppingImpossible()
        if flags & wx.TREE_HITTEST_ONITEMBUTTON:
            self.Expand(item)
        if self.GetSelections() != [item]:
            self.UnselectAll()
            if item != self.GetRootItem(): 
                self.SelectItem(item)
        event.Skip()
        
    def StartDragging(self):
        self.GetMainWindow().Bind(wx.EVT_MOTION, self.OnDragging)
        self.Bind(wx.EVT_TREE_END_DRAG, self.OnEndDrag)
        self.SetCursorToDragging()

    def StopDragging(self):
        self.GetMainWindow().Unbind(wx.EVT_MOTION)
        self.Unbind(wx.EVT_TREE_END_DRAG)
        self.ResetCursor()
        self.UnselectAll()
        self.SelectItem(self._dragItem)
        
    def SetCursorToDragging(self):
        self.GetMainWindow().SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        
    def SetCursorToDroppingImpossible(self):
        self.GetMainWindow().SetCursor(wx.StockCursor(wx.CURSOR_NO_ENTRY))
        
    def ResetCursor(self):
        self.GetMainWindow().SetCursor(wx.NullCursor)

    def IsValidDropTarget(self, dropTarget):
        if dropTarget: 
            allChildren = self.GetItemChildren(self._dragItem, recursively=True)
            parent = self.GetItemParent(self._dragItem) 
            return dropTarget not in [self._dragItem, parent] + allChildren
        else:
            return True        
