#!/usr/bin/env python

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, sys, glob
sys.path.insert(0, '..')
from taskcoachlib import meta
import style


pages = {}
pages['index'] = \
'''        <P><IMG SRC="banner.png" ALT="Banner image"></P>
        <P>%(name)s is a simple open source todo manager to manage personal 
        tasks and todo lists. It grew out of Frank's frustration that well-known 
        task managers, such as those provided with Outlook or Lotus Notes, do
        not provide facilities for composite tasks. Often, tasks and
        other things todo consist of several activities. %(name)s is
        designed to deal with composite tasks.</P>
        <P>%(name)s is developed by Frank Niessink and Jerome Laheurte, with 
        help of different people providing translations. Currently, %(name)s 
        is at version %(version)s. Many people use it on a daily basis, but 
        there are still a lot of 
        features missing. If there's anything you'd like to see included, 
        <a href="https://sourceforge.net/tracker/?group_id=130831&atid=719137">please 
        let us know</a>.
        <P>%(name)s is licensed under the <A HREF="license.html">%(license)s</A> 
        and free to use for both 
        individuals and companies. If %(name)s is a useful product for you, 
        please consider supporting the development of %(name)s. You can support 
        further development by spreading the word, <A HREF="i18n.html">help 
        translate</A> %(name)s in your language, 
        <A HREF="devinfo.html">help develop</A> new features and/or 
        <A HREF="donations.html">donate some money</A> (to help recover 
        costs; any amount is appreciated).</P>
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
            SourceForge. This gets you <A
        HREF="https://sourceforge.net/project/project_donations.php?group_id=130831">listed</A> as donator.
            <LI><form action="https://www.paypal.com/cgi-bin/webscr" method="post">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="image" src="https://www.paypal.com/en_US/i/btn/x-click-but04.gif" border="0" name="submit" alt="Betalingen verrichten met PayPal is snel, gratis en veilig!">
<img alt="" border="0" src="https://www.paypal.com/nl_NL/i/scr/pixel.gif" width="1" height="1">
<input type="hidden" name="encrypted" value="-----BEGIN PKCS7-----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-----END PKCS7-----
">
</form>
        </UL>
        </P>
'''

pages['changes'] = file('changes.html').read()

try:
    md5 = '<P>The MD5 digests for the files are as follows:' + \
        file('md5digests.html').read() + '</P>'
except IOError:
    md5 = ''

prerequisites = '''<a href="http://www.python.org/download/">Python</a> 
<strong>%(pythonversion)s</strong> (or newer)
and <a href="http://www.wxpython.org/download.php">wxPython</a>
<strong>%(wxpythonversion)s</strong> (or newer).'''

pages['download'] = \
'''        <H3>Download %(name)s (release %(version)s)</H3>
        <p>
        <table>
        <tr><td rowspan=4 valign=top><img src="windows.png" alt="Windows"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s-win32.exe">Installer</a> for Microsoft Windows</b></td></tr>
        <tr><td>Windows versions supported: Windows 2000, XP, Vista</td></tr>
        <tr><td>Prerequisites: none.</td></tr>
        <tr><td>Installation: run the installer; it will guide you through
        the installation process.</td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=4 valign=top><img src="mac.png" alt="Mac OS X"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s.dmg">Disk image (dmg)</a> for Mac OS X</b></td></tr>
        <tr><td>Mac OS X versions supported: Mac OS X Tiger/10.4 
        (Universal).</td></tr>
        <tr><td>Prerequisites: none.</td></tr>
        <tr><td>Installation: double click the package and drop the %(name)s 
        application in your programs folder.</td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=5 valign=top><img src="debian.png" alt="Debian"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename_lower)s_%(version)s-1_all.deb">Debian package (deb)</a> for Debian</b></td></tr>
        <tr><td>Prerequisites: ''' + prerequisites + '''
        <tr><td>Installation: 
        Unfortunately Debian does not ship with wxPython 2.8 which is required 
        for %(name)s. You will need to add the wxWidgets repositories to your 
        apt sources list following <a href="http://wiki.wxpython.org/InstallingOnUbuntuOrDebian">these instructions</a>. 
        You can then continue by following the Ubuntu instructions.</td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=5 valign=top><img src="ubuntu.png" alt="Ubuntu"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename_lower)s_%(version)s-1_all.deb">Debian package (deb)</a> for Ubuntu</b></td></tr>
        <tr><td>Prerequisites: ''' + prerequisites + '''
        <tr><td>Installation:
        double click the package to start the installer.</td></tr> 
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=5 valign=top><img src="gentoo.png" alt="Gentoo"></td>
        <td><b><a href="http://packages.gentoo.org/package/app-office/taskcoach">Ebuild</a> for Gentoo</b></td></tr>
        <tr><td>Installation:
        %(name)s is included in Gentoo Portage. Install with emerge:<br>
        <tt>$ emerge taskcoach</tt><td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=5 valign=top><img src="fedora.png" alt="Fedora"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename_lower)s-%(version)s-1.fc8.noarch.rpm">RPM package</a> for Fedora 8</b></td></tr>
        <tr><td>Prerequisites: ''' + prerequisites + '''</td></tr>
        <tr><td>Installation: <tt>$ sudo yum install --nogpgcheck %(filename_lower)s-%(version)s-1.fc8.noarch.rpm</tt></td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=5 valign=top><img src="linux.png" alt="Linux"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s-1.noarch.rpm">RPM package</a> for RPM-based Linux distributions</b></td></tr>
        <tr><td>Prerequisites: ''' + prerequisites + '''</td></tr>
        <tr><td>Installation: use your package manager to install the 
        package</td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=6 valign=top><img src="source.png" alt="Source code"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s-1.src.rpm">Source RPM package</a></b></td></tr>
        <tr><td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s.zip">Source zip archive</a></b></td></tr>
        <tr><td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s.tar.gz">Source tar archive</a></b></td></tr>
        <tr><td>Prerequisites: ''' + prerequisites + '''</td></tr>
        <tr><td>Installation: decompress the archive and run <tt>python 
        setup.py install</tt>. If you have a previous version of %(name)s 
        installed, you may need to force old files to be overwritten: 
        <tt>python setup.py install --force</tt>.</td></tr>
        </table>
        </p>
        <h3>Download previous releases of %(name)s</h3>
        <P>Download previous releases of %(name)s from 
        <A HREF="%(dist_download_prefix)s">Sourceforge</A>.
        </P>
        <h3>MD5 Digests</h3>
''' + md5 

pages['features'] = \
'''        <H3>Features</H3>
        <P>%(name)s currently (%(version)s) has the following features:
        <UL>
            <LI>Creating, editing, and deleting tasks and subtasks.
            <LI>Tasks have a subject, description, priority, start date, 
            due date, a completion date and an optional reminder. Tasks can
            recur on a daily, weekly or monthly basis.
            <LI>Tasks can be viewed as a list or as a tree.
            <LI>Tasks can be sorted by all task attributes, e.g. subject,
            budget, budget left, due date, etc.
            <LI>Several filters to e.g. hide completed tasks or view
            only tasks that are due today. 
            <LI>Tasks can be created by dragging an e-mail message from 
            Outlook or Thunderbird onto a task viewer.
            <LI>Attachments can be added to tasks, notes, and categories by 
            dragging and dropping files, e-mail messages from Outlook or 
            Thunderbird, or URL's onto a task, note or category.
            <LI>Task status depends on its subtask and vice versa. E.g. if 
            you mark the last uncompleted subtask as completed, the parent 
            task is automatically marked as completed too.
            <LI>Tasks and notes can be assigned to user-defined categories. 
            <LI>Settings are persistent and saved automatically. The
            last opened file is loaded automatically when starting
            %(name)s.
            <LI>Tracking time spent on tasks. Tasks can have a budget. 
            Time spent can be viewed by individual effort period, by day, 
            by week, and by month.
            <LI>The %(name)s file format (.tsk) is XML. 
            <LI>Tasks, notes, effort, and categories can be exported to HTML
            and CSV (Comma separated format). Effort can be exported to 
            iCalendar/ICS format as well.
            <LI>Tasks, effort, notes, and categories can be printed. When printing, 
            %(name)s prints the information that is visible in the current
            view, including any filters and sort order. 
            <LI>%(name)s can be run from a removable medium.
            <LI>Tasks and notes can be synchronized via a 
            <a href="http://www.funambol.com/">Funambol</a> server such
            as <a href="http://www.scheduleworld.com">ScheduleWorld</a>.
        </UL>
        <H3>Missing features</H3>
        <P>
        See the list of <A HREF="https://sourceforge.net/tracker/?group_id=130831&atid=719137">requested features</A> 
        for features that people miss.
        </P>'''

pages['license'] = '<PRE>%s</PRE>'%meta.licenseText

pages['screenshots'] = \
'''       <H3>Screenshots</H3>         
        <P>Here are a couple of screenshots from version 0.62 that show 
        the main window, the print preview, and the task editor.</P>
        <P><IMG SRC="screenshot-0.62-treeview.png" ALT="Main window with task tree view"></P>
        <P><IMG SRC="screenshot-0.62-listview.png" ALT="Main window with task list view"></P>
        <P><IMG SRC="screenshot-0.62-printpreview.png" ALT="Print preview"></P>
        <P><IMG SRC="screenshot-0.62-taskeditor.png" ALT="Task editor"></P>'''

pages['i18n'] = \
'''        <H3>Internationalization</H3>
        <H4>Information for users</H4>
        <P>Currently, %(name)s is available in a number of languages: '''\
        + ', '.join(sorted(meta.languages.keys())) + \
        '''. You can select languages via 'Edit' -> 
        'Preferences'. Click the 'Language' icon, select the
        language of your choice and restart %(name)s.</P>
        <H4>Instructions for translators</H4>
        <P>We would welcome translations in additional languages.
        Please be aware that, next to providing the initial translation,
        you will be expected to keep your translation up to date as new
        versions of %(name)s are released.</P>
        <P>A Yahoo!Groups mailinglist is available for discussing the development
        and translation of %(name)s. You can join by sending mail to <tt><a 
        href="mailto:taskcoach-dev-subscribe@yahoogroups.com">taskcoach-dev-subscribe@yahoogroups.com</a></tt>
        or alternatively, if you have a Yahoo id (or don't mind creating one), 
        join via the <a href="http://groups.yahoo.com/group/taskcoach-dev/join">webinterface</a>.</P>

        <P>To create a new translation or update an existing translation, 
        please follow these steps and guidelines:
        <OL>
            <LI>Register at <A HREF="http://launchpad.net">Launchpad</A> and
            don't forget to set your preferred languages, i.e. the language(s)
            you want to translate to.
            <LI>Learn more about 
            <A HREF="http://translations.launchpad.net/+about">translation 
            support by Launchpad</A>.
            <LI>Go to <A HREF="https://launchpad.net/taskcoach">%(name)s at 
            Launchpad</A> and click "Help translate".
            <LI>Start contributing to an existing translation or create a new
            one.
            <LI>Please make sure you understand how
            <A HREF="http://docs.python.org/lib/typesseq-strings.html">Python
            string formatting</A> works since %(name)s uses both the regular
            '%%s' type of string formatting as well as the mapping key form 
            '%%(mapping_key)s'. If string formatting is used in the English
            version of a string, the same formatting should occur in the 
            translated string. In addition, formatting of the form '%%s' 
            needs to be in the same order in the translated string as it is 
            in the English version. Formatting in the form '%%(mapping_key)s'
            can be ordered differently in the translated string than in the 
            English version.
            <LI>Don't translate the string formatting keys: e.g. when you see
            '%%(name)s', don't translate the word 'name'.</LI>
            <LI>Don't translate keyboard shortcuts: e.g. when you see 
            'Shift+Ctrl+V',
            don't translate the words 'Shift' and 'Ctrl', even if your 
            keyboard uses 
            different labels for those keys. Picking a different letter is 
            possible, but please make sure each letter is used only once.</LI>
        </OL>
        </P>'''
        
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
        <p>The mailinglist is also available as the newsgroup 
        <a href="http://dir.gmane.org/gmane.comp.sysutils.pim.taskcoach">gmane.comp.sysutils.pim.taskcoach</a>
        on <a href="http://gmane.org">Gmane</a>.</p>
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
    <P><I>I'm on Windows and when installing a new version of %(name)s the
    installer complains it cannot replace the MSVCP7.dll.</I></P>
    <P>Make sure the old version of %(name)s is not still running, nor 
    any applications started via %(name)s (e.g. a browser started by clicking 
    on a link inside %(name)s).</P>
    <P><I>I'm on Linux and after running taskcoach.py I get the message 
    "ERROR: cannot import the library 'taskcoachlib' " and I was redirected 
    here.</I></P>
    <P>This probably means that the python version you are using to run
    taskcoach.py is different than the python version where the taskcoachlib 
    folder was installed to, and hence python cannot find the library. 
    The taskcoachlib folder is located in 
    /usr/lib/python2.X/site-packages. If you find the taskcoachlib folder and
    run taskcoach.py with the same python version, Task Coach should run. So 
    if taskcoachlib is in /usr/lib/python2.X/site-packages and taskcoach.py is
    located in /usr/bin than 'python2.X /usr/bin/taskcaoch.py' should work. To
    solve this more permanently you can move the taskcoachlib folder to the
    site-packages folder of your default python. To find out what your default
    python is, just start python from the command line, look for the version
    number and then exit with Control-D. Next, move the taskcoachlib folder 
    from its current location to the site-packages folder of your default python
    version as follows (2.D is the version number of your default python
    version, 2.C is the version number where taskcoachlib was installed):
    'mv /usr/lib/python2.C/site-packages/taskcoachlib 
    /usr/lib/python2.D/site-packages'. Now running taskcoach.py should work.</P> 
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
    <P><I>Can I track effort for more than one task at the same
    time?</I></P>
    <P>Yes, when you are tracking effort for a task, select the second
    task, right-click and select 'New effort...'. When you don't fill in
    an end-time, effort for that second task will be tracked too.</P>
    <P><I>How can I mark a task 'inactive'?</I></P>
    <P>Set the start date of the task to a future data or don't set 
    a start date at all by unchecking the start date check box.</P>
    <P><I>How does resizing of columns work?</I>
    <P>In all viewers with columns, the subject column is automatically
    resized to fill up any remaining space. To resize a column, drag the 
    <b>right</b> border of the header of the column you want to resize. If you
    make the subject column wider all other columns will be made
    smaller. If you make the subject column smaller all other columns will be
    made wider. If you make another column wider, the subject column will be 
    made smaller and vice versa.</P>
    <P><I>Can I run Task Coach from a USB stick?</I></P>
    <P>Yes, just install it on a USB stick. In addition, in the files tab of
    the preferences dialog ('Edit' -> 'Preferences'), check 'Save settings 
    (TaskCoach.ini) in the same directory as the program' to make sure your
    settings are saved on the USB stick.</P>
'''

pages['roadmap'] = \
'''    <h3>%(name)s roadmap</h3>
    <p>My aim for %(name)s is to be a personal assistent that helps with
    the daily chores of life: remembering things to do, registering
    hours spent on projects, taking notes, etc. It should also be as
    intuitive as possible for users to deal with and not require any technical
    knowledge.</p>
    <p>Currently, %(name)s knows about four domain concepts: tasks, 
    effort, notes, and categories. A domain concepts that might be added 
    in the future is contact person.</p>
    <p>In the long run, it might be worthwile to allow
    users to add their own concepts. So, for example, if you want to keep
    a list of books to read you could define a book concept and accompanying
    fields like author, title, isbn, read/unread status, etc. That would
    also need the file format to be very flexible.</p>
    <p>Currently, the focus of %(name)s is to support single users. In the long
    run, support for exchange of tasks with other users should be possible,
    probably via the iCalendar standard.</p>
    <p>Anyway, this is it for now, I'll add more as soon as my thoughts
    on the subject crystalize into a more coherent picture of the future 
    direction for %(name)s.</p>
'''

pages['devinfo'] = \
'''    <h3>Information for developers</h3>
    <p>Here's some information for developers that either want to hack
    on %(name)s or reuse code.</p>
    
    <h4>Mailinglist</h4>
    <P>A Yahoo!Groups mailinglist is available for discussing the development
    of %(name)s. You can join by sending mail to <tt><a 
    href="mailto:taskcoach-dev-subscribe@yahoogroups.com">taskcoach-dev-subscribe@yahoogroups.com</a></tt>
    or alternatively, if you have a Yahoo id (or don't mind creating one), 
    join via the <a href="http://groups.yahoo.com/group/taskcoach-dev/join">webinterface</a>.</P>
    <P>You can browse the <a href="http://groups.yahoo.com/group/taskcoach-dev/messages">archive
    of messages</a> without subscribing to the mailinglist.</P>
    <p>The mailinglist is also available as the newsgroup 
    <a href="http://dir.gmane.org/gmane.comp.sysutils.pim.taskcoach.devel">gmane.comp.sysutils.pim.taskcoach.devel</a>
    on <a href="http://gmane.org">Gmane</a>.</p>
    <P>A Sourceforge mailinglist is available for receiving commit messages.
    If you are a %(name)s developer you can <a href="http://lists.sourceforge.net/lists/listinfo/taskcoach-commits">join this mailinglist</a>.
    
    <h4>Dependencies</h4>
    <p>%(name)s is developed in <A HREF="http://www.python.org">Python</A>,
    using <A HREF="http://www.wxpython.org">wxPython</A> for the
    graphical user interface. On Windows, 
    <A HREF="http://sourceforge.net/projects/pywin32/">Pywin32</A> 
    is used as well. For generating the API documentation you need to have
    <A HREF="http://epydoc.sourceforge.net/">Epydoc</A> installed.</p>
    <p>The few other libraries (other than those
    provided by Python, wxPython and Pywin32) that are used are put into the
    taskcoachlib/thirdparty package and included in the source code
    repository.</p>
    
    <h4>Getting the source</h4>
    <p>%(name)s source code is hosted in a <A
    HREF="http://sourceforge.net/svn/?group_id=130831">Subversion repository 
    at SourceForge</A>. You can check out the code from the repository 
    directly or <A HREF="http://taskcoach.svn.sourceforge.net/">browse the
    repository</A>. You can also browse the
    <A HREF="epydoc/index.html">epydoc-generated documentation.</A></p>
    
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
    file, RPM and Debian packages are created and the sources are packaged 
    as compressed archives (.zip and .tar.gz). The Makefile contains targets 
    for each of the distributions. Most of the code for the actual building 
    of the distributions, using the python distutils package, is located in 
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
    <p>I create RPM and DEB packages on Ubuntu (<tt>rpm</tt> and <tt>deb</tt>
    targets) and a Fedora RPM package on Fedora (<tt>fedora</tt> target). 
    Alternatively, Linux users that have installed python and wxPython
    themselves (if not installed by default) can also use the source
    distribution. The source distributions are created by the
    <tt>sdist</tt> Makefile target.</p>
    
    <h4>Coding style</h4>
    <p>Class names are StudlyCaps. Method names are camelCase, except
    for wxPython methods that are called or overridden because those are
    StudlyCaps. At first I thought that was ugly, a mixture of two
    styles. But it turned out to be quite handy, since you can easily
    see whether some method is a wxPython method or not.</p>
    
    <h4>SVN usage conventions</h4>
    <p>Releases are tagged Releasex_y_z (where x has always been 0 so far) 
    and for each Releasex_y_0 a branch (Releasex_y_Branch) is created to
    facilitate bug fix releases. The release tagging and branching is part of 
    the release process as documented in release.py.</p>
    <p>For new big features, feature-specific branches are created to facilitate 
    parallel development, checking in changes while developing, and keep 
    the code on the main trunk releaseable. The process is as follows:</p>
    <ul>
    <li>The feature is discussed on taskcoach-dev.</li>
    <li>If all agree it's a good feature to work on, a
    Feature_&lt;FeatureName&gt;_Branch branch is created and used for
    development of the feature.</li>
    <li>When the feature is done, it is announced on taskcoach-dev.</li>
    <li>The feature is tested on all platforms.</li>
    <li>The changes are merged back to main trunk.</li>
    </ul>
    For small new features, development is done on the trunk, but all unittests
    should succeed before committing.
'''

dist = os.path.join('..', 'website.out')

if not os.path.isdir(dist):
    os.mkdir(dist)

for title, text in pages.items():
    htmlfile = file(os.path.join(dist, '%s.html'%title), 'w')
    text = style.header + text%meta.metaDict + style.footer
    htmlfile.write(text)
    htmlfile.close()

pad = file('pad.xml').read()
padfile = file(os.path.join(dist, 'pad.xml'), 'w')
padfile.write(pad%meta.metaDict)
padfile.close()

import shutil, glob
for file in glob.glob('*.png') + glob.glob('*.ico') + glob.glob('*.css') + \
    ['../icons.in/splash.png']:
    print file
    shutil.copyfile(file, os.path.join(dist, os.path.basename(file)))
