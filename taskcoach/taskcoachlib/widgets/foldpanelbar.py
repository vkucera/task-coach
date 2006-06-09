import wx
import wx.lib.foldpanelbar as foldpanelbar

class FoldPanelBar(foldpanelbar.FoldPanelBar):
    def SetFocus(self):
        expandedPanels = [panel for panel in self._panels \
                          if panel.IsExpanded()]
        for panel in expandedPanels:
            for item in panel._items:
                if item.GetType() == 'WINDOW':
                    item._wnd.SetFocus()
                    return
