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


pages['changes'] = file('changes.html').read()


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
            <LI>Tasks can be sorted by all task attributes, e.g. subject,
            budget, budget left, due date, etc.
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
            <LI>The %(name)s file format (.tsk) is XML. 
        </UL>
        <H3>Missing features</H3>
        Features that you might expect, but are currently missing, are:
        <UL>
            <LI>Reminders
            <LI>Printing
        </UL>
        <H3>Requested features</H3>
        See <A HREF="https://sourceforge.net/tracker/?group_id=130831&atid=719137">feature requests</A>.
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
    ['../icons.in/splash.png']:
    shutil.copyfile(file, os.path.join(dist, os.path.basename(file)))
