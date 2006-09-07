#!/usr/bin/env python

import os, sys, glob
sys.path.append('..')
from taskcoachlib import meta
import style


pages = {}
pages['index'] = \
'''        <P><IMG SRC="banner.png" ALT="Banner image"></P>
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
        <P>Enjoy, %(author)s &lt;%(author_email)s&gt;</P>
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
'''

pages['donations'] = \
'''        <H3>Donations</H3>
        <P>Donations for the development of %(name)s are very much appreciated.
        Options for donating are:
        <UL>
            <LI><A HREF="https://sourceforge.net/donate/index.php?group_id=130831">Donate
            via SourceForge</A>. Fees are deducted for PayPal and 
            SourceForge.
        Peevious donations made via SourceForge are listed <A
        HREF="https://sourceforge.net/project/project_donations.php?group_id=130831">here</A>.
            <LI>Donate directly via <A HREF="http://www.paypal.com">PayPal</A>.
            Please use the email address &lt;%(author_email)s&gt;.</P>
        </UL>
        </P>
'''

pages['changes'] = file('changes.html').read()

pages['download'] = \
'''        <H3>Download %(name)s</H3>
        <P>You can download either the source distribution, in which
        case you need Python <strong>%(pythonversion)s</strong> (or higher) 
        and wxPython <strong>%(wxpythonversion)s</strong> (or higher), or
        you can download an executable distribution for Windows or Mac
        OSX.</P>
        <P>I test %(name)s on Windows XP SP2, Linux Ubuntu 6, and Mac
        OSX 10.4. I'd appreciate some feedback if you are able to run it 
        (or not) on other platforms.</P>
        <P>Download %(name)s from <A HREF="https://sourceforge.net/project/showfiles.php?group_id=130831">Sourceforge</A>.
        </P>
        <P>The MD5 digests for the files are as follows:
''' + file('md5digests.html').read() + '''</P>'''

pages['features'] = \
'''        <H3>Features</H3>
        <P>%(name)s currently (%(version)s) has the following features:
        <UL>
            <LI>Creating, editing, and deleting tasks and subtasks.
            <LI>Tasks have a subject, description, priority, start date, 
            due date, a completion date and an optional reminder.
            <LI>Tasks can be viewed as a list or as a tree.
            <LI>Tasks can be sorted by all task attributes, e.g. subject,
            budget, budget left, due date, etc.
            <LI>Several filters to e.g. hide completed tasks or view
            only tasks that are due today. Filters can be managed through
            the filter side bar.
            <LI>Task status depends on its subtask and vice versa. E.g. if 
            you mark the last uncompleted subtask as completed, the parent 
            task is automatically marked as completed too.
            <LI>Tasks can be assigned to user-defined categories. 
            <LI>Settings are persistent and saved automatically. The
            last opened file is loaded automatically when starting
            %(name)s.
            <LI>Tracking time spent on tasks. Tasks can have a budget. 
            Time spent can be viewed by individual effort period, by day, 
            by week, and by month.
            <LI>The %(name)s file format (.tsk) is XML. 
            <LI>Tasks can be exported to HTML. Effort can be exported to
            XML and iCalendar/ICS format.
            <LI>Tasks and effort can be printed. When printing, Task
            Coach print the information that is visible in the current
            view, including any filters and sort order. 
            <LI>%(name)s can be run from a removable medium.
        </UL>
        <H3>Missing features</H3>
        <P>The main feature that is currently missing is the possibility to
        assign or be assigned tasks to/by other people via the 
        iCalendar standard.
        </P>
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

pages['i18n'] = \
'''        <H3>Internationalization</H3>
        <H4>Information for users</H4>
        <P>Currently, %(name)s is available in a number of languages: '''\
        + ', '.join(meta.languages.keys()) + \
        '''. You can select languages via 'Edit' -> 
        'Preferences'. Click the 'Language' icon, select the
        language of your choice and restart %(name)s.</P>
        <H4>Instructions for translators</H4>
        <P>I would welcome translations in additional languages.
        Please be aware that, next to providing the initial translation,
        you will be expected to keep your translation up to date as new
        versions of %(name)s are released.</P>
        <P>To create a new translation, please follow these steps:
        <OL>
            <LI>Install a gettext catalogs editor. I recommend 
            <A HREF="http://www.poedit.org/">poEdit</A>. 
            <LI>Download the message catalog:
            <A HREF="messages.pot"><TT>messages.pot</TT></A>. This file
            contains all text strings to be translated.
            <LI>Rename <TT>messages.pot</TT> into <TT>yourlanguage.po</TT>.
            <LI>Start poEdit and load <TT>yourlanguage.po</TT> and 
            create the translation. Please make sure you understand how
            <A HREF="http://docs.python.org/lib/typesseq-strings.html">Python
            string formatting</A> works since %(name)s uses both the regular
            '%%s' type of string formatting as well as the mapping key form 
            '%%(mapping_key)s'.
            <LI>Mail me the resulting <TT>yourlanguage.po</TT> file. I will
            include it into %(name)s.
        </OL>
        When a new release of %(name)s is ready, I will make the new
        <A HREF="messages.pot"><TT>messages.pot</TT></A> available here 
        so you can update your <TT>.po</TT> file. This is when using poEdit 
        will really pay off, because it will mark for you which strings have
        been added or changed and require your attention.</P>
        <P>These are the language .po files in the current version
        (%(version)s) of %(name)s:
        <UL>
        ''' + '\n'.join(['<LI><A HREF="%s.po">%s</A></LI>'%(code, language) for
        language, code in meta.languages.items() if language != 'English']) + '</UL></P>'

pages['mailinglist'] = \
'''       <H3>Mailinglist</H3>         
        <P>A Yahoo!Groups mailinglist is available for discussing
        %(name)s. You can join by sending mail to <tt><a 
        href="mailto:taskcoach-subscribe@yahoogroups.com">taskcoach-subscribe@yahoogroups.com</a></tt>
        or alternatively, if you have a Yahoo id (or don't mind creating
        one), join via the <a
        href="http://groups.yahoo.com/group/taskcoach/join">webinterface</a>.</P>
        <P>You can browse the <a
        href="http://groups.yahoo.com/group/taskcoach/messages">archive
        of messages</a> without subscribing to the mailinglist.</P>
'''

pages['faq'] = \
'''    <H3>Frequently asked questions</H3>
    <P><I>I upgraded to a new version and now I cannot load my %(name)s file. It
    says: "Error loading <myfile>.tsk. Are you sure it is a %(name)s file?".
    I'm sure the file's ok. What next?</I></P>
    <P>Remove your TaskCoach.ini file and try again. Sometimes errors in
    loading old settings files will cause %(name)s to barf on .tsk files that
    are just fine. The TaskCoach.ini file is located in C:\Documents and
    Settings\&lt;yourname&gt;\Application Data\TaskCoach if you're on Windows 
    and in /home/&lt;yourname&gt;/.TaskCoach if you're on Linux.</P>
    <P><I>Can I track effort for more than one task at the same
    time?</I></P>
    <P>Yes, when you are tracking effort for a task, select the second
    task, right-click and select 'New effort...'. When you don't fill in
    an end-time, effort for that second task will be tracked too.</P>
    <P><I>I'm on Linux, using a window manager with virtual desktops. If
    I switch (back) to the virtual desktop where %(name)s was running, I can 
    no longer find it. Where did %(name)s go?</I></P>
    <P>%(name)s is probably minimized. Look for the little %(name)s icon
    in the system tray, click on it with your right mouse button and
    select 'Restore'.  Apparently, switching between virtual desktops is
    implemented by sending a minimize event to applications.
    Unfortunately, %(name)s has no way to distinguish between minimize
    events caused by the window manager and minimize events caused by
    the user minimizing the window. If you run into this issue, you may
    want to change the setting 'Hide main window when iconized', see
    'Edit' -> 'Preferences'.</P>
'''

pages['roadmap'] = \
'''    <h3>%(name)s roadmap</h3>
    <p>My aim for %(name)s is to be a personal assistent that helps with
    the daily chores of life: remembering things to do, registering
    hours spent on projects, taking notes, etc. It should also be as
    intuitive as possible for users to deal with and not require any technical
    knowledge.</p>
    <p>Currently, %(name)s knows about two domain concepts: tasks and
    effort. Other domain concepts that might be added include note
    and contact person.</p>
    <p>In the long run, it might be worthwile to allow
    users to add their own concepts. So, for example, if you want to keep
    a list of books to read you could define a book concept and accompanying
    fields like author, title, isbn, read/unread status, etc. That would
    also need the file format to be very flexible.</p>
    <p>Currently, the focus of %(name)s is to support single users. In the long
    run, support for exchange of tasks with other users should be possible,
    probably via the iCal standard.</p>
    <p>Anyway, this is it for now, I'll add more as soon as my thoughts
    on the subject crystalize into a more coherent picture of the future 
    direction for %(name)s.</p>
'''

pages['devinfo'] = \
'''    <h3>Information for developers</h3>
    <p>Here's some information for developers that either want to hack
    on %(name)s or reuse code.</p>
    <h4>Dependencies</h4>
    <p>%(name)s is developed in <A HREF="http://www.python.org">Python</A>,
    using <A HREF="http://www.wxpython.org">wxPython</A> for the
    graphical user interface. The few other libraries (other than those
    provided by Python and wxPython) that are used are put into the
    taskcoachlib/thirdparty package and included in the CVS
    repository.</p>
    <h4>Getting the source</h4>
    <p>%(name)s source code is hosted at <A
    HREF="https://sourceforge.net/cvs/?group_id=130831">SourceForge</A>.
    You can check out the code from CVS directly or <A
    HREF="http://taskcoach.cvs.sourceforge.net/taskcoach/">browse the
    repository</A>.</p>
    <h4>Tests</h4>
    <p>Tests can be run from the Makefile. There are targets for
    <tt>unittests</tt>, <tt>integrationtests</tt>,
    <tt>releasetests</tt>, and <tt>alltests</tt>. These targets all
    invoke the tests/test.py script. Run <tt>tests/test.py --help</tt> for 
    many more test options (including profiling, timing, measuring test 
    coverage, etc.).</p>
    <h4>Building the distributions</h4>
    <p>The Makefile is used to build the different distributions of
    %(name)s. Currently, a Windows installer is built, a Mac OSX dmg
    file, and the sources are packaged as compressed archives (.zip and 
    .tar.gz). The Makefile contains targets for each of the
    distributions. Most of the code for the actual building of the
    distributions, using the python distutils package, is located in 
    make.py. In turn, make.py imports setup.py. These two files were
    split so that setup.py only contains distutils information related
    to <i>installing</i>, while make.py contains all information related
    to <i>building</i> the distributions. Only setup.py is included in
    the source distributions.</p>
    <h5>Windows</h5>
    <p>On Windows, py2exe is used to bundle the application with the python
    interpreter and wxPython libraries. Innosetup is used to create an
    executable installer. 
    All the necessary packaging code is in make.py
    and driven from the Makefile (<tt>windist</tt> target).</p>
    <h5>Mac OSX</h5>
    <p>On Mac OSX, py2app is used to bundle the application. The resulting
    application is packaged into a dmg file using the <tt>hdiutil</tt>
    utility, which is part of Mac OSX. 
    All the necessary packaging code is in make.py
    and driven from the Makefile (<tt>macdist</tt> target).</p>
    <h5>Linux</h5>
    <p>Currently, Linux users have to install python and wxPython
    themselves (if not installed by default) and use the source
    distribution. The source distributions are created by the
    <tt>sdist</tt> Makefile target.</p>
    <h4>Coding style</h4>
    <p>Class names are StudlyCaps. Method names are camelCase, except
    for wxPython methods that are called or overridden because those are
    StudlyCaps. At first I thought that was ugly, a mixture of two
    styles. But it turned out to be quite handy, since you can easily
    see whether some method is a wxPython method or not.</p>
'''

dist = os.path.join('..', 'website.out')

if not os.path.isdir(dist):
    os.mkdir(dist)

for title, text in pages.items():
    htmlfile = file(os.path.join(dist, '%s.html'%title), 'w')
    text = style.header + text%meta.metaDict + style.footer
    htmlfile.write(text)
    htmlfile.close()

import shutil, glob
for file in glob.glob('*.png') + glob.glob('*.ico') + glob.glob('*.css') + \
    glob.glob('../i18n.in/*.po') + ['../i18n.in/messages.pot', 
    '../icons.in/splash.png']:
    print file
    shutil.copyfile(file, os.path.join(dist, os.path.basename(file)))
