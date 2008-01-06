import meta
from i18n import _
from tips import showTips

_TOC = _('''<h3>Table of contents</h3>
<ul>
<li><a href="#tasks">Tasks</a>
    <ul>
        <li><a href="#abouttasks">About tasks</a></li>
        <li><a href="#taskproperties">Task properties</a></li>
        <li><a href="#taskstates">Task states</a></li>
        <li><a href="#taskcolors">Task colors</a></li>
    </ul>
</li>
<li><a href="#effort">Effort</a>
    <ul>
        <li><a href="#abouteffort">About effort</a></li>
        <li><a href="#effortproperties">Effort properties</a></li>
    </ul>
</li>
<li><a href="#categories">Categories</a>
    <ul>
        <li><a href="#aboutcategories">About categories</a></li>
        <li><a href="#categoryproperties">Category properties</a></li>
    </ul>
</ul>
''')

_taskSection = _('''<h3><a name="tasks">Tasks</a></h3>
''')

_aboutTasksSubsection = _('''<h4><a name="abouttasks">About tasks</a></h4>
 
<p>Tasks are the basic objects that you manipulate. Tasks can
represent anything from a simple little thing you have to do, like buying a gift
for your loved one, to a complete project, consisting of different phases, and
numerous activities.</p>
''')

_taskPropertiesSubsection = _('''<h4><a name="taskproperties">Task 
properties</a></h4>

<p>Tasks have the following properties you can change:
<ul>
<li>Subject: a single line that summarizes the task.</li>
<li>Description: a multi-line description of the task.</li>
<li>Due date: the date the task should be finished. This can be 'None' 
indicating that this task has no fixed due date.</li>
<li>Start date: the first date on which the task can be started. The start date 
defaults to the date the task is created. It can also be 'None' indicating that
you don't really want to start this task. This can be convenient for e.g. 
registering sick leave.</li>
<li>Completion date: this date is 'None' as long as the task has not been 
completed. It is set to the current date when you mark the task as completed. 
The completion date can also be entered manually.</li>
<li>Budget: amount of hours available for the task.</li>
<li>Hourly fee: the amount of money earned with the task per hour.</li>
<li>Fixed fee: the amount of money earned with the task regardless of the time
spent.</li>
</ul></p>

<p>The following properties are calculated from the properties above:
<ul>
<li>Days left: the number of days left until the due date.</li>
<li>Total budget: sum of task budget and the budgets of all subtasks of the 
task, recursively.</li>
<li>Time spent: effort spent on the task.</li>
<li>Total time spent: effort spent on the task and all subtasks, 
recursively.</li>
<li>Budget left: task budget minus time spent on the task.</li>
<li>Total budget left: total task budget minus total time spent.</li>
<li>Total fixed fee: sum of fixed fee of the task and the fixed fees of all 
subtasks of the task, recursively.</li>
<li>Revenue: hourly fee times hours spent plus fixed fee.</li>
<li>Total revenue: sum of task revenue and revenue of all subtasks, 
recursively.</li>
</ul></p>
''')

_taskStatesSubsection = _('''<h4><a name="taskstates">Task states</a></h4>

<p>Tasks always have exactly one of the following states:
<ul>
<li>Active: the start date is in the past and the due date in the future;</li>
<li>Inactive: the start date is in the future, or</li>
<li>Completed: the task has been completed.</li>
</ul></p>

<p>In addition, tasks can be referenced as:
<ul>
<li>Over due: the due date is in the past;</li>
<li>Due today: the due date is today;</li>
<li>Over budget: no buget left;</li>
<li>Under budget: still budget left;</li>
<li>No budget: the task has no budget.</li>
</ul></p>
 ''')

_taskColorsSubsection = _('''<h4><a name="taskcolors">Task colors</a></h4>

<p>The text of tasks is colored according to the following rules:
<ul>
<li>Over due tasks are red;</li>
<li>Tasks due today are orange;</li>
<li>Active tasks are black text with a blue icon;</li>
<li>Future tasks are gray, and</li>
<li>Completed tasks are green.</li>
</ul>
This all assumes you have not changed the text colors through the preferences 
dialog, of course.</p>
<p>The background color of tasks is determined by the categories the task
belongs to, see the section about 
<a href="#categoryproperties">category properties</a> below.</p>
''')

_effortSection = _('''<h3><a name="effort">Effort</a></h3>
''')

_aboutEffortSubsection = _('''<h4><a name="abouteffort">About effort</a></h4>

<p>Whenever you spent time on tasks, you can record the amount of time
spent by tracking effort. Select a task and invoke 'Start tracking effort' in
the Effort menu or the context menu or via the 'Start tracking effort' toolbar 
button.</p>
''')

_effortPropertiesSubsection = _('''<h4><a name="effortproperties">Effort
properties</a></h4>

<p>Effort records have the following properties you can change:
<ul>
<li>Task: the task the effort belongs to.</li>
<li>Start date/time: start date and time of the effort.</li>
<li>Stop date/time: stop date and time of the effort. This can be 'None' as 
long as you are still working on the task.</li>
<li>Description: a multi-line description of the effort.</li>
</ul></p>

<p>The following properties are calculated from the properties above:
<ul>
<li>Time spent: how much time you have spent working on the task.</li>
<li>Total time spent: sum of time spent on the task and all subtasks, 
recursively.</li>
<li>Revenue: money earned with the time spent.</li>
<li>Total revenue: money earned with the total time spent.</li>
</ul></p>
''')

_categorySection = _('''<h3><a name="categories">Categories</a></h3>
''')

_aboutCategoriesSubSection = _('''<h4><a name="aboutcategories">About 
categories</a></h4>

<p>Tasks may belong to one or more categories. First, you need to create the
category that you want to use via the 'Category' menu. Then, you can add a task to
one or more categories by editing the task and checking the relevant categories
for that task in the category pane of the task editor.</p>

<p>You can limit the tasks shown in the task viewers to one or more categories
by checking a category in the category viewer. For example, if you have a 
category 'phone calls' and you check that category, the task viewers will 
only show tasks belonging to that category; in other words the phone calls 
you need to make.</p>
''')

_categoryPropertiesSubSection = _('''<h4><a name="categoryproperties">Category 
properties</a></h4>

<p>Categories have a subject, a description, and a color. The color is used
to render the background of the category and the background of tasks that
belong to that category. If a category has no color of its own, but it has
a parent category with a color, the parent's color will be used.  
If a task belongs to multiple categories that each have a color associated with
them, a mixture of the colors will be used to render the background of that
task.</p>
''')

helpHTML = _TOC + _taskSection + _aboutTasksSubsection + \
    _taskPropertiesSubsection + _taskStatesSubsection + _taskColorsSubsection + \
    _effortSection + _aboutEffortSubsection + _effortPropertiesSubsection + \
    _categorySection + _aboutCategoriesSubSection + _categoryPropertiesSubSection
    
aboutHTML = _('''<h4>%(name)s - %(description)s</h4>
<h5>Version %(version)s, %(date)s</h5>
<p>By %(author)s <%(author_email)s><p>
<p><a href="%(url)s" target="_blank">%(url)s</a></p>
<p>%(copyright)s</p>
<p>%(license)s</p>
''')%meta.metaDict

doubleline = '================================================================\n'

header = doubleline + '%(name)s - %(description)s\n'%meta.metaDict + doubleline

aboutText = header + _('''
Version %(version)s, %(date)s

By %(author)s <%(author_email)s>

%(url)s

%(copyright)s
%(license)s

''')%meta.metaDict + doubleline

installText = header + '''

--- Prerequisites ----------------------------------------------

You need Python version %(pythonversion)s or higher and wxPython 
version %(wxpythonversion)s or higher.


--- Testing ----------------------------------------------------

Before installing, you may want to run the unittests included.
Issue the following command:

  cd tests; python test.py

If all goes well, you should see a number of dots appearing and
the message 'Ran X tests in Y seconds. OK'. If not, you'll get
one or more failed tests. In that case, please run the tests
again, redirecting the output to a textfile, like this:

  python test.py 2> errors.txt

Please mail me the errors.txt file and your platform information
(operating system version, Python version and wxPython version).


--- Installation -----------------------------------------------

There are two options to install %(name)s: 

First, you can simply move this directory to some suitable 
location and run taskcoach.py (or taskcoach.pyw if you are on 
the Windows platform) from there.

Alternatively, you can use the Python distutils setup script
to let Python install %(name)s for you. In that case run the
following command:

  python setup.py install

If you have a previous version of %(name)s installed, you may
need to force old files to be overwritten, like this:

  python setup.py install --force

'''%meta.metaDict + doubleline

buildText = header + '''

--- Building ---------------------------------------------------

To be done.

'''%meta.metaDict + doubleline
