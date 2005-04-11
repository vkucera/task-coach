#!/usr/bin/env python

import os, sys
sys.path.append('..')
from taskcoachlib import meta
import style


pages = {}
pages['index'] = \
'''        <IMG SRC="banner.png" ALT="Banner image"><BR>
        <P>%(name)s is a simple open source todo manager to manage personal 
        tasks and todo lists. It grew out of my frustration that well-known 
        task managers, such as those provided with Outlook or Lotus Notes, do
        not provide facilities for composite tasks. Often, tasks and
        other things todo consist of several activities. %(name)s is
        designed to deal with composite tasks.</P>
        <P>Currently, %(name)s is at version %(version)s. I use it on a daily
        basis, but there are still a lot of features missing. If there's
        anything you'd like to see included, please let me know.
        <P>You might want to see some <A
        HREF="screenshots.html">screenshots</A>, read the <A
        HREF="license.html">license</A> (which is the %(license)s) or 
        <A HREF="download.html">download</A> %(name)s.</P>
        <P>%(name)s is developed using a number of open source products.
        See <A HREF="credits.html">credits</A> for details.</P>
        <H3>Enjoy, %(author)s &lt;%(author_email)s&gt;</H3>
        '''

pages['credits'] = \
'''        <H3>Credits</H3>
        <P>%(name)s depends on a number of other, open source, software
        packages. It is developed in <A
        HREF="http://www.python.org">Python</A>. The user interface uses
        <A HREF="http://www.wxpython.org">wxPython</A>. The icons are from
        the great <A HREF="http://www.icon-king.com">Nuvola icon set</A> by 
        David Vignoni. The Windows installer is <A
        HREF="http://www.jrsoftware.org">Inno Setup</A>. %(name)s source
        code and releases are hosted by <A
        HREF="http://sourceforge.net/">Sourceforge</A>.</P>
        <P>Donations to %(name)s are much appreciated. Donations are listed 
        <A HREF="https://sourceforge.net/project/project_donations.php?group_id=130831">here</A>
        at Sourceforge.</P>
'''


pages['changes'] = \
'''        <H3>Change history</H3>
        <H4>Release 0.30 - April 11, 2005</H4>
        Bugs fixed:
        <UL>
        <LI>More than one task due today would crash Task Coach 
        (<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=1180641&group_id=130831&atid=719134">1180641</A>).
        </UL>
        <H4>Release 0.29 - April 10, 2005</H4>
        Bugs fixed:
        <UL>
        <LI>New effort in the context menu did not work in release 0.28 
        (<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=1178562&group_id=130831&atid=719134">1178562</A>).
        <LI>When selecting 'View' -> 'Completed tasks' in the task tree, only
        completed root tasks were hidden 
        (<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=1179372&group_id=130831&atid=719134">1179372</A>).
        </UL> 
        Features added:
        <UL>
        <LI>What tab is active is now a persistent setting. This includes 
        the tabs and choices in the mainwindow and the effort choices in 
        the task editor 
        (<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=1178779&group_id=130831&atid=719137">1178779</A>).
        <LI>Reordered 'View' -> 'Tasks due before end of' menu 
        (<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=1178880&group_id=130831&atid=719137">1178880</A>).
        <LI>Added a separate 'Budget' tab in the task editor.
        <LI>Taskbar icon now indicates whether task effort tracking is on 
        (<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=1178057&group_id=130831&atid=719137">1178057</A>).
        <LI>Effort is sorted from most recent to least recent 
        (<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=1179332&group_id=130831&atid=719137">1179332</A>).
        <LI>Changed task/subtask separator in the task list view from '|' 
        to ' -> ' 
        (<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=1179374&group_id=130831&atid=719137">1179374</A>).
        </UL>
        <H4>Release 0.28 - April 6, 2005</H4>
        Bugs fixed:
        <UL>
        <LI>Hitting return or double click to edit effort in the task editor 
        now works 
        (<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=1172164&group_id=130831&atid=719134">1172164</A>).
        <LI>Subtasks with the same name would only be visible once in the task 
        tree view.
        </UL>
        Features added:
        <UL>
        <LI>You can hide composite tasks in the task list view so that only 
        leaf tasks are visible. Menu item 'View' -> 'Tasks with subtasks'. 
        Requested by Brian Crounse.
        </UL>
        <H4>Release 0.27 - April 4, 2005</H4>
        Features added:
        <UL>
        <LI>Tasks can have a budget.
        </UL>
        <H4>Release 0.26 - March 28, 2005</H4>
        Bugs fixed:
        <UL>
        <LI>Marking a task completed did not stop effort tracking (<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=1159918&group_id=130831&atid=719134">1159918</A>).
        <LI>Reading lots of efforts was slow.
        </UL>
        Features added:
        <UL>
        <LI>Save button is disabled when saving is not necessary, 
        requested by Mike Vorozhbensky (<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=1164472&group_id=130831&atid=719137">1164472</A>).
        <LI>Effort records have a description field, requested by Kent 
        (<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=1167147&group_id=130831&atid=719137">1167147</A>).
        </UL>
        <H4>Release 0.25 - March 13, 2005</H4>
        Bugs fixed:
        <UL>
        <LI>The menu item 'Effort' -&gt; 'New effort' did not work in
        release 0.24.
        </UL>
        Features added:
        <UL>
        <LI>XML export now includes effort records.
        <LI>Effort per day, per week and per month view now also show 
        total time spent (i.e. time including time spent on subtasks).
        </UL>
        <H4>Release 0.24 - March 10, 2005</H4>
        Bugs fixed:
        <UL>
        <LI>Saving a selection of tasks to a separate file would also save 
        all effort records to that file (instead of just the effort records 
        for the selected tasks), giving errors when loading that file.
        <LI>Deleting a task with effort records would not delete the
        effort records.
        </UL>
        Features added:
        <UL>
        <LI>The tracking status of tasks is saved. So if you start tracking a
        task, quit Task Coach, and restart Task Coach later, effort for that 
        task is still being tracked. Requested by Bob Hossley.
        </UL>
        <H4>Release 0.23 - February 20, 2005</H4>
        Bugs fixed:
        <UL>
        <LI>Fixed a couple of bugs in the unit tests, discovered
        by Stephen Boulet and Jerome Laheurte on the Linux platform.
        </UL>
        <H4>Release 0.22 - February 17, 2005</H4>
        Bugs fixed:
        <UL>
        <LI>In the effort summary view, effort spent on a task in the same 
        month or week but in different years would erroneously be added. 
        E.g. effort in January 2004 and January 2006 would be added. 
        <LI>The mechanism to prevent effort periods with a negative duration 
        (i.e.  a start time later than the stop time) in the effort editor was
        invoked on each key stroke which caused inconvenient behaviour. Fixed
        it by only invoking it when the user leaves the text or combo box.
        </UL>
        Features added:
        <UL>
        <LI>Added possibility to start tracking effort for a task, with start 
        time equal to the end time of the previous effort period. This is for
        example convenient if you stop working on a task and then spend
        some time deciding on what to do next. This is the 'Start tracking 
        from last stop time' menu item in the 'Effort' menu.
        <LI>(Re)Added the unittests to the source distribution. 
        See INSTALL.txt.
        <LI>Export to XML. Currently limited to tasks, effort is not 
        exported yet.
        </UL>
        <H4>Release 0.21 - February 9, 2005</H4>
        Bugs fixed:
        <UL>
        <LI>Setting the start date/time in the effort editor would change the 
        stop date/time while not strictly necessary to prevent negative 
        durations.
        <LI>Refreshing the virtual ListCtrl failed under 
        wxPython2.5-gtk2-unicode-2.5.3.1-fc2_py2.3 and 
        wxPython-common-gtk2-unicode-2.5.3.1-fc2_py2.3. Reported by Stephen 
        Boulet. 
        <LI>After iconizing the main window for a second time, the icon in the
        task bar wouldn't be hidden anymore. Reported and fixed by Jerome
        Laheurte.
        </UL>
        <H4>Release 0.20 - February 6, 2005</H4>
        Bugs fixed:
        <UL>
        <LI>Reading .tsk files version 2 failed.
        <LI>Completed child tasks were not hidden in the tree view when
        'View->Completed tasks' was on.
        <LI>Hiding the find panel did not clear the search filter.
        <LI>When searching for tasks, not all matches were shown in the tree 
        view.
        <LI>Displaying time spent and total time spent in the list view for 
        more than a dozen tasks and efforts was slow. Used caching to speed 
        it up.
        <LI>Tool tips on the toolbar included mnemonics and accelerator 
        characters on Linux. Reported on python-2.3.4 and 
        wxPython2.5-gtk2-unicode-2.5.3.1-fc2_py2.3 on Suse 9.2 by
        Stephen Boulet.
        </UL>
        Features added:
        <UL>
        <LI>Effort can be viewed summarized per day, per week, and per month.
        <LI>Effort for a specific task can be viewed (and edited) in the task 
        editor.
        <LI>Effort tracking can be stopped from the taskbar menu.
        <LI>Size and position of the main window are saved in the settings 
        and restored on the next session. This also includes whether the 
        main window is iconized or not.
        <LI>Splash screen can be turned off.
        </UL>
'''

pages['download'] = \
'''        <H3>Download %(name)s</H3>
        <P>You can download either the source distribution, in which
        case you need Python <strong>%(pythonversion)s</strong> (or higher) 
        and wxPython <strong>%(wxpythonversion)s</strong> (or higher), or
        you can download the Windows executable distribution.</P>
        <P>I am only able to test %(name)s on Windows XP at the moment, so I'd 
        appreciate some feedback if you are able to run it (or not) on other
        platforms.</P>
        <P>
        <TABLE>
        <TR>
            <TD><A HREF="%(filename)s-%(version)s-win32.exe">%(filename)s-%(version)s-win32.exe</A></TD>
            <TD>Installer for Windows XP (and other Windows versions)</TD>
        </TR>
        <TR>
            <TD><A HREF="%(filename)s-%(version)s.zip">%(filename)s-%(version)s.zip</A></TD>
            <TD>Zipped source distribution</TD>
        </TR>
        <TR>
            <TD><A HREF="%(filename)s-%(version)s.tar.gz">%(filename)s-%(version)s.tar.gz</A></TD>
            <TD>Tarred/gzipped source distribution</TD>
        </TR>
        </TABLE>
        <P>Download from <A HREF="https://sourceforge.net/project/showfiles.php?group_id=130831">Sourceforge</A>.'''

pages['features'] = \
'''        <H3>Features</H3>
        <P>%(name)s currently (%(version)s) has the following features:
        <UL>
            <LI>Creating, editing, and deleting tasks and subtasks.
            <LI>Tasks have a subject, description, start date, due date and a 
            completion date.
            <LI>Tasks can be viewed as a list or as a tree.
            <LI>Tasks are sorted by due date.
            <LI>Several filters to e.g. hide completed tasks or view
            only tasks that are due today. 
            <LI>Task status depends on its subtask and vice versa. E.g. if 
            you mark the last uncompleted subtask as completed, the parent 
            task is automatically marked as completed too.
            <LI>Settings are persistent and saved automatically. The
            last opened file is loaded automatically when starting
            %(name)s.
            <LI>Track time spent on tasks. Tasks can have a budget. 
            Time spent can be viewed by individual effort period, by day, 
            by week, and by month.
            <LI>Export of tasks to XML. 
        </UL>
        <H3>Missing features</H3>
        Features that you might expect, but are currently missing, are:
        <UL>
            <LI>Reminders
            <LI>Printing
        </UL>
        <H3>Requested features</H3>
        Features requested or suggested by people. The more people 
        request a feature, the bigger the chance I will add it in the 
        next release (hint).
        <UL>
            <LI>A graphics view of the tasks, like horizontal bars 
            representing the tasks duration, with a dates row at the top 
            so you can see the start and end dates (the same type of 
            view you can get in Outlook). Requested by Nadia.
            <LI>Original time estimation, current time estimation,
            elapsed time, remaining time. Suggested by Sander Boom.
            <LI>Priorities per task (at least five levels). Suggested by
            Sander Boom.
            <LI>Export to HTML. Suggested by Sander Boom.
            <LI>Start tracking tasks from the task bar tray
            icon popu menu. Suggested by Wolfgang Keller.
        </UL>
        </P>'''

pages['license'] = '<PRE>%s</PRE>'%meta.licenseText

pages['screenshots'] = \
'''       <H3>Screenshots</H3>         
        <P>Here are a couple of screenshots from version 0.22 that show 
        the list view, the task view, the effort view and the task editor.</P>
        <P><IMG SRC="screenshot-0.22-listview.png" ALT="List view"></P>
        <P><IMG SRC="screenshot-0.22-treeview.png" ALT="Tree view"></P>
        <P><IMG SRC="screenshot-0.22-effortview.png" ALT="Effort view"></P>
        <P><IMG SRC="screenshot-0.22-taskeditor.png" ALT="Task editor"></P>'''

dist = os.path.join('..', 'dist')

if not os.path.isdir(dist):
    os.mkdir(dist)

for title, text in pages.items():
    htmlfile = file(os.path.join(dist, '%s.html'%title), 'w')
    text = style.header + text%meta.metaDict + style.footer
    htmlfile.write(text)
    htmlfile.close()

import shutil, glob
for file in glob.glob('*.png') + glob.glob('*.ico') + glob.glob('*.css') + \
    ['../icons/splash.png']:
    shutil.copyfile(file, os.path.join(dist, os.path.basename(file)))
