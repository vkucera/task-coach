import meta
from i18n import _


colorsText = _('''Tasks are colored according to the following rules:
- Over due tasks are red;
- Tasks due today are orange;
- Active tasks are black;
- Future tasks are gray, and
- Completed tasks are green.
''')

tasksText = _('''Tasks have the following properties:
- Subject: a single line that summarizes the task.
- Description: a multi-line description of the task.
- Due date: the date the task should be finished. This can be 'None' indicating that this task has no fixed due date.
- Start date: the first date on which the task can be started. The start date defaults to the date the task is created.
- Completed: a flag that indicates whether the task is completed or not.
- Completion date: this date is None as long as the task has not been completed. It is set to the current date when the user marks the task as completed. The completion date can also be entered manually.
- Budget: amount of hours available for the task.

Tasks always have exactly one of the following states:
- Active: the start date is in the past and the due date in the future;
- Inactive: the start date is in the future, or
- Completed: the task has been completed.

In addition, tasks can be referenced as:
- Over due: the due date is in the past;
- Due today: the due date is today;
- Over budget: no buget left;
- Under budget: still budget left;
- No budget: the task has no budget.
''')

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

  python test.py

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

'''%meta.metaDict + doubleline

buildText = header + '''

--- Building ---------------------------------------------------

To be done.

'''%meta.metaDict + doubleline
