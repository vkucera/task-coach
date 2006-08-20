import viewer, viewercontainer
from i18n import _

def _addEffortViewers(viewerContainer, taskList, uiCommands, settings):
    effortViewer = viewer.EffortListViewer(viewerContainer, taskList, 
        uiCommands, settings)
    viewerContainer.addViewer(effortViewer, _('Effort list'), 'start')
    effortPerDayViewer = viewer.EffortPerDayViewer(viewerContainer,
        taskList, uiCommands, settings)
    viewerContainer.addViewer(effortPerDayViewer, _('Effort per day'), 'date')
    effortPerWeekViewer = viewer.EffortPerWeekViewer(viewerContainer,
        taskList, uiCommands, settings)
    viewerContainer.addViewer(effortPerWeekViewer, _('Effort per week'), 
        'date')
    effortPerMonthViewer = viewer.EffortPerMonthViewer(viewerContainer,
        taskList, uiCommands, settings)
    viewerContainer.addViewer(effortPerMonthViewer, _('Effort per month'), 
        'date')
    
def addEffortViewers(viewerContainer, taskList, uiCommands, settings, setting):
    effortViewerContainer = viewercontainer.ViewerChoicebook(viewerContainer, 
        settings, setting)
    _addEffortViewers(effortViewerContainer, taskList, uiCommands, 
        settings)
    viewerContainer.addViewer(effortViewerContainer, _('Effort'), 'start')

def addTaskViewers(viewerContainer, taskList, uiCommands, settings):
    listViewer = viewer.TaskListViewer(viewerContainer, taskList, 
        uiCommands, settings)
    viewerContainer.addViewer(listViewer, _('Task list'), 'listview')
    treeListViewer = viewer.TaskTreeListViewer(viewerContainer, taskList,
        uiCommands, settings)
    viewerContainer.addViewer(treeListViewer, _('Task tree'), 'treeview')
        
