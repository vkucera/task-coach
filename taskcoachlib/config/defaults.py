import meta

defaults = { \
'view': { \
    'statusbar': 'True',
    'toolbar': '(22, 22)',
    'mainviewer': '0',               # Index of active viewer in main window
    'effortviewerintaskeditor': '0', # Index of active effort viewer in task editor
    'tasklistviewercount': '1',      # Number of task list viewers in main window
    'tasktreeviewercount': '0',      # (This viewer is currently not used)
    'tasktreelistviewercount': '1',  # Number of task tree list viewers in main window
    'categoryviewercount': '1',      # etc.
    'noteviewercount': '0',
    'effortlistviewercount': '1',
    'effortperdayviewercount': '1',
    'effortperweekviewercount': '0',
    'effortpermonthviewercount': '0',
    'language': 'en_US',
    'taskcategoryfiltermatchall': 'True'},
'tasklistviewer': { \
    'sortby': 'dueDate',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'columns': "['startDate', 'dueDate']",
    'columnsalwaysvisible': "['subject']",
    'tasksdue': 'Unlimited',
    'hidecompletedtasks': 'False',
    'hideinactivetasks': 'False',
    'hideactivetasks': 'False',
    'hideoverduetasks': 'False',
    'hideoverbudgettasks': 'False',
    'hidecompositetasks': 'False', },
'tasktreeviewer': { \
    'sortby': 'dueDate',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'tasksdue': 'Unlimited',
    'hidecompletedtasks': 'False',
    'hideinactivetasks': 'False',
    'hideactivetasks': 'False',
    'hideoverduetasks': 'False',
    'hideoverbudgettasks': 'False' },
'tasktreelistviewer': { \
    'sortby': 'dueDate',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'columns': "['startDate', 'dueDate']",
    'columnsalwaysvisible': "['subject']",
    'tasksdue': 'Unlimited',
    'hidecompletedtasks': 'False',
    'hideinactivetasks': 'False',
    'hideactivetasks': 'False',
    'hideoverduetasks': 'False',
    'hideoverbudgettasks': 'False' },
'categoryviewer': { \
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'noteviewer': { \
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'columns': "[]",
    'columnsalwaysvisible': "['subject']" },
'effortlistviewer': { \
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortlistviewerintaskeditor': { \
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortperdayviewer': { \
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortperdayviewerintaskeditor': { \
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortperweekviewer': { \
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortperweekviewerintaskeditor': { \
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortpermonthviewer': { 
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortpermonthviewerintaskeditor': { 
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'window': { \
    'size': '(600, 500)',
    'position': '(-1, -1)',
    'iconized': 'False',
    'starticonized': 'WhenClosedIconized', # 'Never', 'Always', 'WhenClosedIconized'
    'splash': 'True',
    'hidewheniconized': 'False',
    'hidewhenclosed': 'False',
    'tips': 'True',
    'tipsindex': '0',
    'blinktaskbariconwhentrackingeffort': 'True' },
'file': { \
    'recentfiles': '[]',
    'maxrecentfiles': '4',
    'lastfile': '',
    'autosave': 'False',
    'backup': 'False',
    'saveinifileinprogramdir': 'False' },
'color': { \
    'activetasks': '(0, 0, 0)',
    'completedtasks': '(0, 255, 0)',
    'overduetasks': '(255, 0, 0)',
    'inactivetasks': '(192, 192, 192)',
    'duetodaytasks': '(255, 128, 0)' },
'editor': { \
    'maccheckspelling': 'True' },
'version': { \
    'notified': meta.data.version,
    'notify': 'True' },
'behavior': { \
    'markparentcompletedwhenallchildrencompleted': 'True' },
'feature': { \
    'notes': 'True' }}
