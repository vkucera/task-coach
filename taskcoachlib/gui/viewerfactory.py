import viewer, viewercontainer
from i18n import _

def _addEffortViewers(viewerContainer, effortList, uiCommands):
    effortViewer = viewer.EffortListViewer(viewerContainer, effortList, 
        uiCommands)
    viewerContainer.addViewer(effortViewer, _('Effort list'), 'start')
    effortPerDayViewer = viewer.EffortPerDayViewer(viewerContainer,
        effortList, uiCommands)
    viewerContainer.addViewer(effortPerDayViewer, _('Effort per day'), 'date')
    effortPerWeekViewer = viewer.EffortPerWeekViewer(viewerContainer,
        effortList, uiCommands)
    viewerContainer.addViewer(effortPerWeekViewer, _('Effort per week'), 'date')
    effortPerMonthViewer = viewer.EffortPerMonthViewer(viewerContainer,
        effortList, uiCommands)
    viewerContainer.addViewer(effortPerMonthViewer, _('Effort per month'), 'date')
    
def addEffortViewers(viewerContainer, effortList, uiCommands, settings, setting):
    effortViewerContainer = viewercontainer.ViewerChoicebook(viewerContainer, settings, setting)
    _addEffortViewers(effortViewerContainer, effortList, uiCommands)
    viewerContainer.addViewer(effortViewerContainer, _('Effort'), 'start')

def addTaskViewers(viewerContainer, filteredTaskList, uiCommands, settings):
    listViewer = viewer.TaskListViewer(viewerContainer, filteredTaskList, 
        uiCommands, settings)
    viewerContainer.addViewer(listViewer, _('Task list'), 'listview')
    treeViewer = viewer.TaskTreeViewer(viewerContainer, filteredTaskList, 
        uiCommands)
    viewerContainer.addViewer(treeViewer, _('Task tree'), 'treeview')
    if False:
        ganttChartViewer = viewer.GanttChartViewer(viewerContainer, filteredTaskList,
            uiCommands)
        viewerContainer.addViewer(ganttChartViewer, _('Gantt chart'))
        