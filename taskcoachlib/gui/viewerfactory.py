import viewer, viewercontainer

def _addEffortViewers(viewerContainer, effortList, uiCommands):
    effortViewer = viewer.EffortListViewer(viewerContainer, effortList, 
        uiCommands)
    viewerContainer.addViewer(effortViewer, 'Effort list', 'start')
    effortPerDayViewer = viewer.EffortPerDayViewer(viewerContainer,
        effortList, uiCommands)
    viewerContainer.addViewer(effortPerDayViewer, 'Effort per day', 'date')
    effortPerWeekViewer = viewer.EffortPerWeekViewer(viewerContainer,
        effortList, uiCommands)
    viewerContainer.addViewer(effortPerWeekViewer, 'Effort per week', 'date')
    effortPerMonthViewer = viewer.EffortPerMonthViewer(viewerContainer,
        effortList, uiCommands)
    viewerContainer.addViewer(effortPerMonthViewer, 'Effort per month', 'date')
    
def addEffortViewers(viewerContainer, effortList, uiCommands):
    effortViewerContainer = viewercontainer.ViewerChoicebook(viewerContainer)
    _addEffortViewers(effortViewerContainer, effortList, uiCommands)
    viewerContainer.addViewer(effortViewerContainer, 'Effort', 'start')

def addTaskViewers(viewerContainer, filteredTaskList, effortList, uiCommands):
    listViewer = viewer.TaskListViewer(viewerContainer, filteredTaskList, 
        effortList, uiCommands)
    viewerContainer.addViewer(listViewer, 'Task list', 'listview')
    treeViewer = viewer.TaskTreeViewer(viewerContainer, filteredTaskList, 
        effortList, uiCommands)
    viewerContainer.addViewer(treeViewer, 'Task tree', 'treeview')
        