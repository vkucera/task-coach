import wx

class TreeCtrl(wx.TreeCtrl):
    def __init__(self, parent, getItemText, getItemImage, getItemAttr,
            getItemChildrenCount, getItemFingerprint, selectcommand, 
            editcommand, popupmenu=None):
        super(TreeCtrl, self).__init__(parent, -1, style=wx.TR_HIDE_ROOT|\
            wx.TR_MULTIPLE|wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT)
        self.selectcommand = selectcommand
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelect)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, editcommand.onCommandActivate)
        if popupmenu:
            self.popupmenu = popupmenu
            self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.onPopup)
        self.getItemText = getItemText
        self.getItemImage = getItemImage
        self.getItemAttr = getItemAttr
        self.getItemChildrenCount = getItemChildrenCount
        self.getItemFingerprint = getItemFingerprint
        self.refresh(0)
        self.fingerprint = {}
        
    def curselection(self):
        return [self.GetPyData(item) for item in self.GetSelections()]

    def onPopup(self, event):
        self.PopupMenu(self.popupmenu, event.GetPoint())

    def onSelect(self, event):
        self.selectcommand()

    def refresh(self, count):
        self.validItems = []
        if count == 0:
            self.DeleteAllItems()
            self.AddRoot('root')
        else:
            index = 0
            root = self.GetRootItem()
            while index < count:
                index = self.addItemsRecursively(root, index)
            self.deleteUnusedItems()
        
    def addItemsRecursively(self, parent, index):
        node = self.AppendItem(parent, index)
        nextIndex = index + 1
        for i in range(self.getItemChildrenCount(index)):
            nextIndex = self.addItemsRecursively(node, nextIndex)
        return nextIndex     
            
    def renderNode(self, node, index):
        normalImageIndex, expandedImageIndex = self.getItemImage(index) 
        self.SetItemImage(node, normalImageIndex, wx.TreeItemIcon_Normal)
        self.SetItemImage(node, expandedImageIndex, 
            wx.TreeItemIcon_Expanded)
        self.SetItemTextColour(node, self.getItemAttr(index).GetTextColour())
        
    def AppendItem(self, parent, index):
        fingerprint = self.getItemFingerprint(index)
        item = self.findItem(parent, fingerprint)
        if not item:
            insertAfterChild = self.findInsertionPoint(parent)
            if insertAfterChild:
                item = self.InsertItem(parent, insertAfterChild, 
                    self.getItemText(index))
            else:
                item = self.PrependItem(parent, self.getItemText(index))
            self.renderNode(item, index)
        self.SetPyData(item, index)
        self.validItems.append(item.m_pItem)
        self.fingerprint[item.m_pItem] = fingerprint
        return item

    def findInsertionPoint(self, parent):
        insertAfterChild = None
        for child in self.getChildren(parent):
            if child.m_pItem in self.validItems:
                insertAfterChild = child
        return insertAfterChild

    def findItem(self, parent, fingerprint):
        for child in self.getChildren(parent):
            if self.fingerprint[child.m_pItem] == fingerprint:
                return child
        return None        

    def deleteUnusedItems(self):
        unusedItems = []
        for item in self.getChildren(recursively=True):
            if item.m_pItem not in self.validItems:
                del self.fingerprint[item.m_pItem]
                unusedItems.append(item)
        for item in unusedItems:
            self.Delete(item)
                
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
            index = self.GetPyData(item)
            self.SelectItem(item, index in indices)
            if index in indices:
                self.EnsureVisible(item)

    def __getitem__(self, index):
        for item in self.getChildren(recursively=True):
            if self.GetPyData(item) == index:
                return item
        raise IndexError

