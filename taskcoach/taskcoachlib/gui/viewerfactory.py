import viewer, viewercontainer
from i18n import _

def _addEffortViewers(viewerContainer, effortList, taskList, uiCommands, settings):
    effortViewer = viewer.EffortListViewer(viewerContainer, effortList, 
        uiCommands, settings, taskList=taskList)
    viewerContainer.addViewer(effortViewer, _('Effort list'), 'start')
    effortPerDayViewer = viewer.EffortPerDayViewer(viewerContainer,
        effortList, uiCommands, settings, taskList=taskList)
    viewerContainer.addViewer(effortPerDayViewer, _('Effort per day'), 'date')
    effortPerWeekViewer = viewer.EffortPerWeekViewer(viewerContainer,
        effortList, uiCommands, settings, taskList=taskList)
    viewerContainer.addViewer(effortPerWeekViewer, _('Effort per week'), 'date')
    effortPerMonthViewer = viewer.EffortPerMonthViewer(viewerContainer,
        effortList, uiCommands, settings, taskList=taskList)
    viewerContainer.addViewer(effortPerMonthViewer, _('Effort per month'), 'date')
    
def addEffortViewers(viewerContainer, effortList, taskList, uiCommands, settings, setting):
    effortViewerContainer = viewercontainer.ViewerChoicebook(viewerContainer, settings, setting)
    _addEffortViewers(effortViewerContainer, effortList, taskList, uiCommands, settings)
    viewerContainer.addViewer(effortViewerContainer, _('Effort'), 'start')

def addTaskViewers(viewerContainer, filteredTaskList, uiCommands, settings):
    listViewer = viewer.TaskListViewer(viewerContainer, filteredTaskList, 
        uiCommands, settings)
    viewerContainer.addViewer(listViewer, _('Task list'), 'listview')
    treeListViewer = viewer.TaskTreeListViewer(viewerContainer, filteredTaskList, 
        uiCommands, settings)
    viewerContainer.addViewer(treeListViewer, _('Task tree'), 'treeview')
        