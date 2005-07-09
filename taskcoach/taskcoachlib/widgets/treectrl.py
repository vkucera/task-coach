import wx
       

class TreeCtrl(wx.TreeCtrl):
    def __init__(self, parent, getItemText, getItemImage, getItemAttr,
            getItemChildrenCount, getItemId, getItemChildIndex,
            selectcommand, editcommand, popupmenu=None):
        super(TreeCtrl, self).__init__(parent, -1, style=wx.TR_HIDE_ROOT|\
            wx.TR_MULTIPLE|wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT)
        self.selectcommand = selectcommand
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelect)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.onExpand)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self.onCollapse)
        self.editcommand = editcommand
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, editcommand.onCommandActivate)
        # We deal with double clicks ourselves, to prevent the default behaviour
        # of collapsing or expanding nodes on double click. 
        self.Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)
        if popupmenu:
            self.popupmenu = popupmenu
            self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.onPopup)
        self.getItemText = getItemText
        self.getItemImage = getItemImage
        self.getItemAttr = getItemAttr
        self.getItemChildrenCount = getItemChildrenCount
        self.getItemId = getItemId
        self.getItemChildIndex = getItemChildIndex
        self.refresh(0)
        
    def curselection(self):
        return [self.index(item) for item in self.GetSelections()]

    def onPopup(self, event):
        self.PopupMenu(self.popupmenu, event.GetPoint())

    def onSelect(self, event):
        if not self._refreshing:
            self.selectcommand()

    def onDoubleClick(self, event):
        if not self.isCollapseExpandButtonClicked(event):
            self.editcommand.onCommandActivate(event)
        event.Skip(False)
        
    def onExpand(self, event):
        item = event.GetItem()
        itemIndex = self.index(item)
        childIndex = itemIndex + 1
        nextItemIndex = childIndex + self.getItemChildrenCount(itemIndex, recursive=True)
        while childIndex < nextItemIndex:
            childIndex = self.addItemsRecursively(item, childIndex)
        
    def onCollapse(self, event):
        self.CollapseAndReset(event.GetItem())
        
    def isCollapseExpandButtonClicked(self, event):
        item, flags = self.HitTest(event.GetPosition())
        return flags & wx.TREE_HITTEST_ONITEMBUTTON

    def refresh(self, count):
        self._refreshing = True
        self._count = count
        self._validItems = []
        self.itemsToExpandOrCollapse = {}
        self.Freeze()
        if count == 0:
            self.DeleteAllItems()
            self.AddRoot('root')
        else:
            index = 0
            root = self.GetRootItem()
            while index < count:
                index = self.addItemsRecursively(root, index)
            self.deleteUnusedItems()
            self.restoreCollapseExpandState()
        self.Thaw()
        self._refreshing = False
        
    def addItemsRecursively(self, parent, index):
        node = self.AppendItem(parent, index)
        nextIndex = index + 1
        if self.IsExpanded(node):
            for i in range(self.getItemChildrenCount(index)):
                nextIndex = self.addItemsRecursively(node, nextIndex)
        else:
            nextIndex += self.getItemChildrenCount(index, recursive=True)
            if self.getItemChildrenCount(index) > 0 and not self.ItemHasChildren(node):
                self.SetItemHasChildren(node)
        return nextIndex     
            
    def renderNode(self, node, index):
        normalImageIndex, expandedImageIndex = self.getItemImage(index) 
        self.SetItemImage(node, normalImageIndex, wx.TreeItemIcon_Normal)
        self.SetItemImage(node, expandedImageIndex, 
            wx.TreeItemIcon_Expanded)
        self.SetItemTextColour(node, self.getItemAttr(index).GetTextColour())
        
    def AppendItem(self, parent, index):
        itemId = self.getItemId(index)
        oldItem = self.findItem(itemId)
        if oldItem and self.itemUnchanged(oldItem, index) and \
                self.GetItemParent(oldItem) == parent:
            newItem = oldItem
        else:
            insertAfterChild = self.findInsertionPoint(parent)
            if insertAfterChild:
                newItem = self.InsertItem(parent, insertAfterChild, 
                    self.getItemText(index))
            else:
                newItem = self.PrependItem(parent, self.getItemText(index))
            self.renderNode(newItem, index)
            if not oldItem and parent != self.GetRootItem():
                self.itemsToExpandOrCollapse[parent] = True
            if oldItem:
                self.itemsToExpandOrCollapse[newItem] = self.IsExpanded(oldItem)
                if self.getItemChildrenCount(index) > self.GetPyData(oldItem)[2]:
                    self.itemsToExpandOrCollapse[newItem] = True
        self.SetPyData(newItem, self.itemFingerprint(index))
        self._validItems.append(newItem)
        return newItem
    
    def itemFingerprint(self, index):
        return (index, self.getItemId(index),  
            self.getItemChildrenCount(index), self.getItemImage(index), self.getItemText(index),
            self.getItemAttr(index), self.getItemChildIndex(index))
            
    def itemUnchanged(self, item, index):
        oldIndex, oldId, oldChildrenCount, oldImage, oldText,\
            oldAttr, oldChildIndex = self.GetPyData(item)
        return self.getItemChildIndex(index) == oldChildIndex and\
            self.getItemImage(index) == oldImage and self.getItemText(index) == oldText and\
            self.getItemAttr(index).GetTextColour() == oldAttr.GetTextColour()

    def findInsertionPoint(self, parent):
        insertAfterChild = None
        for child in self.getChildren(parent):
            if child in self._validItems:
                insertAfterChild = child
        return insertAfterChild

    def findItem(self, itemId):
        for child in self.getChildren(recursively=True):
            if self.GetPyData(child)[1] == itemId:
                return child
        return None        

    def deleteUnusedItems(self):
        unusedItems = []
        for item in self.getChildren(recursively=True):
            if item not in self._validItems:
                unusedItems.append(item)
        for item in unusedItems:
            self.Delete(item)
        
    def restoreCollapseExpandState(self):
        for item, expand in self.itemsToExpandOrCollapse.items():
            if expand:
                self.Expand(item)
            else:
                self.CollapseAndReset(item)
                
    def getChildren(self, parent=None, recursively=False):
        if not parent:
            parent = self.GetRootItem()
        child, cookie = self.GetFirstChild(parent)
        while child.IsOk():
            yield (child)
            if recursively:
                for grandchild in self.getChildren(child, recursively):
                    yield (grandchild)
            child, cookie = self.GetNextChild(parent, cookie)
        
    def GetItemCount(self):
        return self.GetCount()

    def clearselection(self):
        self.UnselectAll()
        self.selectcommand()

    def selectall(self):
        for item in self.getChildren(recursively=True):
            self.SelectItem(item)
        self.selectcommand()

    def invertselection(self):
        for item in self.getChildren(recursively=True):
            self.ToggleItemSelection(item)
        self.selectcommand()

    def select(self, indices):
        for item in self.getChildren(recursively=True):
            index = self.index(item)
            self.SelectItem(item, index in indices)
            if index in indices:
                self.EnsureVisible(item)
        self.selectcommand()

    def __getitem__(self, index):
        for item in self.getChildren(recursively=True):
            if self.index(item) == index:
                return item
        raise IndexError

    def index(self, item):
        return self.GetPyData(item)[0]
    
    def expandAllItems(self):
        for item in self.getChildren(recursively=True):
            self.Expand(item)

    def collapseAllItems(self):
        for item in self.getChildren():
            self.CollapseAndReset(item)
            
    def expandSelectedItems(self):
        for item in self.GetSelections():
            self.Expand(item)
            for child in self.getChildren(item, recursively=True):
                self.Expand(child)
                
    def collapseSelectedItems(self):
        for item in self.GetSelections():
            self.CollapseAndReset(item)
