import viewer, wx
from i18n import _

    
def addEffortViewers(viewerContainer, taskList, uiCommands, settings):
    _addViewers(viewerContainer, viewer.EffortListViewer, (taskList, 
                uiCommands, settings), {}, 'start', settings)
    _addViewers(viewerContainer, viewer.EffortPerDayViewer, (taskList, 
                uiCommands, settings), {}, 'date', settings)
    _addViewers(viewerContainer, viewer.EffortPerWeekViewer, (taskList, 
                uiCommands, settings), {}, 'date', settings)
    _addViewers(viewerContainer, viewer.EffortPerMonthViewer, (taskList, 
                uiCommands, settings), {}, 'date', settings)

def addTaskViewers(viewerContainer, taskList, uiCommands, settings, categories):
    _addViewers(viewerContainer, viewer.TaskListViewer, (taskList, uiCommands,
                settings), dict(categories=categories), 'listview', settings)
    _addViewers(viewerContainer, viewer.TaskTreeListViewer, (taskList,
                uiCommands, settings), dict(categories=categories), 
                'treeview', settings)

def addCategoryViewers(viewerContainer, categoryContainer, uiCommands, 
                       settings):
    _addViewers(viewerContainer, viewer.CategoryViewer, (categoryContainer, 
                uiCommands, settings), {}, 'category', settings)
    
def addNoteViewers(viewerContainer, noteContainer, uiCommands, settings, categories):
    _addViewers(viewerContainer, viewer.NoteViewer, (noteContainer, uiCommands,
                settings), dict(categories=categories), 'note', settings)

def _addViewers(viewerContainer, viewerClass, viewerArgs, viewerKwArgs, 
                bitmap, settings):
    numberOfViewersToAdd = settings.getint('view', 
        viewerClass.__name__.lower() + 'count')
    for i in range(numberOfViewersToAdd):
        viewerInstance = viewerClass(viewerContainer, *viewerArgs, **viewerKwArgs)
        viewerContainer.addViewer(viewerInstance, viewerInstance.title(), bitmap)