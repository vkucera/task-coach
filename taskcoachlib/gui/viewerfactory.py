import viewer, wx
from i18n import _

    
def addEffortViewers(viewerContainer, taskList, uiCommands, settings):
    _addViewers(viewerContainer, viewer.EffortListViewer, (taskList, 
                uiCommands, settings), {}, _('Effort details'), 'start', 
                settings)
    _addViewers(viewerContainer, viewer.EffortPerDayViewer, (taskList, 
                uiCommands, settings), {}, _('Effort per day'), 'date', 
                settings)
    _addViewers(viewerContainer, viewer.EffortPerWeekViewer, (taskList, 
                uiCommands, settings), {}, _('Effort per week'), 'date', 
                settings)
    _addViewers(viewerContainer, viewer.EffortPerMonthViewer, (taskList, 
                uiCommands, settings), {}, _('Effort per month'), 'date', 
                settings)

def addTaskViewers(viewerContainer, taskList, uiCommands, settings, categories):
    _addViewers(viewerContainer, viewer.TaskListViewer, (taskList, uiCommands,
                settings), dict(categories=categories), _('Task list'), 
                'listview', settings)
    _addViewers(viewerContainer, viewer.TaskTreeListViewer, (taskList,
                uiCommands, settings), dict(categories=categories), 
                _('Task tree'), 'treeview', settings)

def addCategoryViewers(viewerContainer, categoryContainer, uiCommands, 
                       settings):
    _addViewers(viewerContainer, viewer.CategoryViewer, (categoryContainer, 
                uiCommands, settings), {}, _('Categories'), 'category', settings)
    
def addNoteViewers(viewerContainer, noteContainer, uiCommands, settings):
    _addViewers(viewerContainer, viewer.NoteViewer, (noteContainer, uiCommands,
                settings), {}, _('Notes'), 'note', settings)

def _addViewers(viewerContainer, viewerClass, viewerArgs, viewerKwArgs, title, 
                bitmap, settings):
    numberOfViewersToAdd = settings.getint('view', 
        viewerClass.__name__.lower() + 'count')
    for i in range(numberOfViewersToAdd):
        viewerInstance = viewerClass(viewerContainer, *viewerArgs, **viewerKwArgs)
        viewerContainer.addViewer(viewerInstance, title, bitmap)