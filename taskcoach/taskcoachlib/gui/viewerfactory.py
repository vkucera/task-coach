import viewer
from i18n import _

    
def addEffortViewers(viewerContainer, taskList, uiCommands, settings):
    effortViewer = viewer.EffortListViewer(viewerContainer, taskList, 
        uiCommands, settings)
    viewerContainer.addViewer(effortViewer, _('Effort details'), 'start')
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

def addTaskViewers(viewerContainer, taskList, uiCommands, settings, categories):
    listViewer = viewer.TaskListViewer(viewerContainer, taskList, 
        uiCommands, settings, categories=categories)
    viewerContainer.addViewer(listViewer, _('Task list'), 'listview')
    treeListViewer = viewer.TaskTreeListViewer(viewerContainer, taskList,
        uiCommands, settings, categories=categories)
    viewerContainer.addViewer(treeListViewer, _('Task tree'), 'treeview')

def addCategoryViewers(viewerContainer, categoryContainer, uiCommands, 
                       settings):
    categoryViewer = viewer.CategoryViewer(viewerContainer, categoryContainer,
                                           uiCommands, settings)
    viewerContainer.addViewer(categoryViewer, _('Categories'), 'category')
