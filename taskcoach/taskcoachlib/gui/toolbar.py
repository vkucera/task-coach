import wx, uicommand 

class ToolBar(wx.ToolBar, uicommand.UICommandContainer):
    def __init__(self, window, uiCommands, size=(32, 32)):
        super(ToolBar, self).__init__(window, style=wx.TB_TEXT)
        self.SetToolBitmapSize(size) 
        self.appendUICommands(uiCommands, self.commandNames())
        self.Realize()

    def commandNames(self):
        return ['open', 'save', None, 'undo', 'redo', None, 'cut', 'copy', 
            'paste', None, 'new', 'newsubtask', 'edit', 'markcompleted', 
            'delete', None, 'starteffort', 'stopeffort']
        
    def AppendSeparator(self):
        ''' This little adapter is needed for 
        uicommand.UICommandContainer.appendUICommands'''
        self.AddSeparator()

    def appendUICommand(self, uiCommand):
        return uiCommand.appendToToolBar(self)
