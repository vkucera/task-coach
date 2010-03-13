#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Frank Niessink <frank@niessink.com>
Copyright (C) 2008-2009 Jerome Laheurte <fraca7@free.fr>

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

import os, sys, glob, shutil, wx
sys.path.insert(0, '..')
from taskcoachlib import meta
import style
try:
    import md5digests
    md5digests = md5digests.md5digests
except ImportError:
    md5digests = dict()
    

pages = {}
pages['index'] = \
u'''        <P><IMG SRC="images/banner.png" ALT="Banner image"></P>
        <P>%(name)s is a simple open source todo manager to keep track of
        personal tasks and todo lists. It grew out of a frustration that
        most task managers do not provide facilities for composite tasks.
        Often, tasks and other things todo consist of several activities.
        %(name)s is designed to deal with composite tasks. In addition, it offers
        effort tracking, categories, and notes. %(name)s is available for Windows,
        Mac OS X, Linux, and iPhone and iPod Touch.</P>
        <P>%(name)s is developed by Frank Niessink and Jérôme Laheurte, with
        help of different people providing translations. Currently, %(name)s 
        is at version %(version)s. Many people use it on a daily basis, but 
        there are still a lot of features missing. If there's anything you'd
        like to see included, <a href="http://taskcoach.uservoice.com/"
        onClick="javascript: pageTracker._trackPageview('/outgoing/uservoice.com/desktop');">please 
        let us know</a>.</P>
        <P>%(name)s is licensed under the <A HREF="license.html">%(license)s</A> 
        and free to use for both 
        individuals and companies. If %(name)s is a useful product for you, 
        please consider supporting the development of %(name)s. You can support 
        further development by spreading the word, <A HREF="i18n.html">help 
        translate</A> %(name)s in your language, 
        <A HREF="devinfo.html">help develop</A> new features and/or 
        <A HREF="donations.html">donate some money</A> (to help recover 
        costs; any amount is appreciated).</P>
        <P>%(name)s is developed using a number of products, see 
        credits at the left.</P>
        <P>Enjoy, <a href="mailto:%(author_email)s">%(author_unicode)s</a></P>
        <!-- AppStoreHQ:claim_code:258f8973d401112a215d79afdb82fef934ee56c9 -->
        <!-- AppStoreHQ:developer_claim_code:d28c5a79965194fd06870ec80ab83114356b664d -->
        '''

pages['donations'] = \
'''        <H3>Donations</H3>
        <P>Donations for the development of %(name)s are very much appreciated.
        Options for donating are:
        <UL>
            <LI><A HREF="https://sourceforge.net/donate/index.php?group_id=130831" onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/donate');">Donate
            via SourceForge</A>. Fees are deducted for PayPal and 
            SourceForge. This gets you <A
        HREF="https://sourceforge.net/project/project_donations.php?group_id=130831" onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/donaters');">listed</A> as donator.
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


pages['changes'] = file('changes.html').read().decode('UTF-8')
pages['changes'] += '<P><A HREF="all_changes.html">View complete change history</A></P>'
pages['all_changes'] = file('all_changes.html').read().decode('UTF-8')


prerequisites = '''
              <a href="http://www.python.org/download/" 
                 onClick="javascript: pageTracker._trackPageview('/outgoing/python.org/download');">Python</a> 
              <strong>%(pythonversion)s</strong> and 
              <a href="http://www.wxpython.org/download.php" 
                 onClick="javascript: pageTracker._trackPageview('/outgoing/wxpython.org/download');">wxPython</a>
              <strong>%(wxpythonversion)s</strong> (or newer)'''


def download_header(platform=None, release=None, warning=None):
    title = 'Download %(name)s'
    if release:
        title += ' release %s'%release
    if platform:
        title += ' for %s'%platform
    if not warning:
        warning = '''%(name)s is currently alpha-state software. 
          This means that %(name)s contains bugs. We do our best to prevent 
          bugs and fix them as soon as possible. Still, we strongly advise you 
          to make backups of your work on a regular basis, and especially before 
          upgrading.'''
    return '        <h3>%s</h3>\n'%title + \
'''        <p>
          <b>A word of warning:</b> ''' + warning + '\n        </p>'
          

def download_table(**kwargs):
    filename = kwargs['download_url'].split('/')[-1]%meta.metaDict
    md5 = md5digests.get(filename, '')
    kwargs['rows'] = 5 if md5 else 4
    kwargs['md5'] = '\n            <tr><td>MD5 digest: %s.</td></tr>'%md5 if md5 else ''
    # Deal with platforms that are not a name but 'all platforms':
    platform = kwargs['platform']
    kwargs['platform_versions'] = 'Platforms' if platform == 'all platforms' else platform + ' versions'
    return '''        <p>
          <table>
            <tr>
              <td rowspan=%(rows)s valign=top>
                <img src="images/%(image)s.png" alt="%(image)s">
              </td>
              <td>
                <b>
                  <a href="%(download_url)s" 
                     onClick="javascript: pageTracker._trackPageview('/outgoing/download/%(platform_lower)s');">%(package_type)s</a> for %(platform)s
                </b>
              </td>
            </tr>
            <tr><td>%(platform_versions)s supported: %(platform_versions_supported)s.</td></tr>
            <tr><td>Prerequisites: %(prerequisites)s.</td></tr>
            <tr><td>Installation: %(installation)s.</td></tr>%(md5)s
          </table>
        </p>'''%kwargs


windowsOptions = dict(platform='Microsoft Windows',
                      platform_lower='windows',
                      platform_versions_supported='Windows 2000, XP, Vista, Windows 7',
                      prerequisites='none')

windowsInstaller = download_table(image='windows',
                                  download_url='%(dist_download_prefix)s/%(filename)s-%(version)s-win32.exe',
                                  package_type='Installer',
                                  installation='run the installer; it will guide you through the installation process',
                                  **windowsOptions)
 
windowsPortableApp = download_table(image='portableApps',
                                    download_url='%(dist_download_prefix)s/%(filename)sPortable_%(version)s.paf.exe',
                                    package_type='TaskCoachPortable portable app',
                                    installation='run the installer; it will guide you through the installation process',
                                    **windowsOptions)

windowsPenPack = download_table(image='winPenPack',
                                download_url='%(dist_download_prefix)s/X-%(filename)s_%(version)s_rev1.zip',
                                package_type='winPenPack portable app',
                                installation='unzip the archive contents in the location where you want %(name)s to be installed',
                                **windowsOptions) 
  
sep = '\n        <hr>\n'

pages['download_for_windows'] = sep.join([download_header(platform='Microsoft Windows',
                                                          release='%(version)s'), 
                                          windowsInstaller, windowsPortableApp, 
                                          windowsPenPack]) 


macDMG = download_table(image='mac',
                        download_url='%(dist_download_prefix)s/%(filename)s-%(version)s.dmg',
                        package_type='Disk image (dmg)',
                        platform='Mac OS X', platform_lower='macosx',
                        platform_versions_supported='Mac OS X Tiger/10.4 (Universal) and later',
                        prerequisites='none',
                        installation='double click the package and drop the %(name)s application in your programs folder')

pages['download_for_mac'] = sep.join([download_header(platform='Mac OS X',
                                                      release='%(version)s'), 
                                                      macDMG])


debian = download_table(image='debian', 
                        download_url='%(dist_download_prefix)s/%(filename_lower)s_%(version)s-1_all.deb',
                        package_type='Debian package (deb)',
                        platform='Debian', platform_lower='debian',
                        platform_versions_supported='Debian GNU/Linux 4.0 ("etch") and later',
                        prerequisites=prerequisites + ''' If your Debian 
              installation does not have the minimally required wxPython version 
              you will need to install it yourself following 
              <a href="http://wiki.wxpython.org/InstallingOnUbuntuOrDebian">these 
              instructions</a>''',
                        installation='double click the package to start the installer')

ubuntu = download_table(image='ubuntu',
                        download_url='%(dist_download_prefix)s/%(filename_lower)s_%(version)s-1_all.deb',
                        package_type='Debian package (deb)',
                        platform='Ubuntu', platform_lower='ubuntu',
                        platform_versions_supported='Ubuntu 8.04 LTS ("Hardy Heron") and later',
                        prerequisites=prerequisites + ''' If your Ubuntu 
              installation does not have the minimally required wxPython version 
              you will need to install it yourself following 
              <a href="http://wiki.wxpython.org/InstallingOnUbuntuOrDebian">these 
              instructions</a>''',
                        installation='double click the package to start the installer')

gentoo = download_table(image='gentoo',
                        download_url='http://packages.gentoo.org/package/app-office/taskcoach',
                        package_type='Ebuild',
                        platform='Gentoo', platform_lower='gentoo',
                        platform_versions_supported='Gentoo 2008.0 and later',
                        prerequisites=prerequisites,
                        installation='%(name)s is included in Gentoo Portage. Install with emerge: <tt>$ emerge taskcoach</tt>')

opensuse = download_table(image='opensuse',
                          download_url='(dist_download_prefix)s/%(filename_lower)s-%(version)s-1.opensuse.noarch.rpm',
                          package_type='RPM package',
                          platform='OpenSuse', platform_lower='opensuse',
                          platform_versions_supported='OpenSuse 11.2',
                          prerequisites=prerequisites,
                          installation='double click the package to start the installer')

fedora8 = download_table(image='fedora',
                         download_url='%(dist_download_prefix)s/%(filename_lower)s-%(version)s-1.fc8.noarch.rpm',
                         package_type='RPM package',
                         platform='Fedora', platform_lower='fedora',
                         platform_versions_supported='Fedora 8-10',
                         prerequisites=prerequisites,
                         installation='<tt>$ sudo yum install --nogpgcheck %(filename_lower)s-%(version)s-1.fc*.noarch.rpm</tt>')

fedora11 = download_table(image='fedora',
                          download_url='%(dist_download_prefix)s/%(filename_lower)s-%(version)s-1.fc11.noarch.rpm',
                          package_type='RPM package',
                          platform='Fedora', platform_lower='fedora',
                          platform_versions_supported='Fedora 11 and later',
                          prerequisites=prerequisites,
                          installation='<tt>$ sudo yum install --nogpgcheck %(filename_lower)s-%(version)s-1.fc*.noarch.rpm</tt>')

linux = download_table(image='linux',
                       download_url='%(dist_download_prefix)s/%(filename)s-%(version)s-1.noarch.rpm',
                       package_type='RPM package',
                       platform='Linux', platform_lower='rpm',
                       platform_versions_supported='All Linux versions that support RPM and the prerequisites',
                       prerequisites=prerequisites,
                       installation='use your package manager to install the package')

pages['download_for_linux'] = sep.join([download_header(platform='Linux',
                                                        release='%(version)s'), 
                                        debian, ubuntu, gentoo, opensuse,
                                        fedora8, fedora11, linux])


iphone = download_table(image='appstore',
                        download_url='http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewSoftware?id=311403563&mt=8',
                        package_type='%(name)s App',
                        platform='iPhone and iPod Touch', platform_lower='appstore',
                        platform_versions_supported='iPhone or iPod Touch with iPhone OS 2.2.1 or later',
                        prerequisites='none',
                        installation='buy %(name)s from the AppStore via iTunes or your iPhone or iPod Touch')
                        
pages['download_for_iphone'] = sep.join([download_header(platform='iPhone and iPod Touch',
                                                         release='1.1'), 
                                         iphone])


sourceOptions = dict(image='source', prerequisites=prerequisites,
                     installation='''decompress the archive and run <tt>python 
              setup.py install</tt>. If you have a previous version of %(name)s 
              installed, you may need to force old files to be overwritten: 
              <tt>python setup.py install --force</tt>''')

source_rpm = download_table(download_url='%(dist_download_prefix)s/%(filename)s-%(version)s-1.src.rpm',
                            package_type='Source RPM package',
                            platform='Linux', platform_lower='source_rpm',
                            platform_versions_supported='All Linux platforms that support RPM and the prerequisites',
                            **sourceOptions)

source_zip = download_table(download_url='%(dist_download_prefix)s/%(filename)s-%(version)s.zip',
                            package_type='Source zip archive',
                            platform='all platforms', platform_lower='source_zip',
                            platform_versions_supported='All platforms that support the prerequisites',
                            **sourceOptions)

source_tgz = download_table(download_url='%(dist_download_prefix)s/%(filename)s-%(version)s.tar.gz',
                            package_type='Source tar archive',
                            platform='all platforms', platform_lower='source_gz',
                            platform_versions_supported='All platforms that support the prerequisites',
                            **sourceOptions)

subversion = download_table(image='sources',
                            download_url='http://sourceforge.net/projects/taskcoach/develop',
                            package_type='Sources from Subversion',
                            platform='all platforms', platform_lower='subversion',
                            platform_versions_supported='All platforms that support the prerequisites',
                            prerequisites=prerequisites,
                            installation='''run <tt>make prepare</tt> to generate 
              the icons and language files and then <tt>python taskcoach.py</tt> 
              to start the application''')


pages['download_sources'] = sep.join([download_header(release='%(version)s'), 
                                      source_rpm, source_zip, 
                                      source_tgz, subversion])


buildbotOptions = dict(platform='all platforms', 
                       platform_versions_supported='See the different download sections',
                       prerequisites='See the different download sections',
                       installation='See the different download sections')

latest_bugfixes = download_table(image='bug',
                                 download_url='http://www.fraca7.net/TaskCoach-packages/latest_bugfixes.py',
                                 package_type='Latest bugfixes',
                                 platform_lower='latest_bugfixes',
                                 **buildbotOptions)

latest_features = download_table(image='latest_features', 
                                 download_url='http://www.fraca7.net/TaskCoach-packages/latest_features.py',
                                 package_type='Latest features',
                                 platform_lower='latest_features',
                                 **buildbotOptions)

warning = '''          These packages are automatically generated by our <a
        href="http://www.fraca7.net:8010/waterfall">buildbot</a> each
        time a change is checked in the source tree. This is bleeding
        edge, use at your own risk.'''
        
pages['download_daily_build'] = sep.join([download_header(warning=warning), 
                                          latest_bugfixes, latest_features])

old_releases = download_table(image='archive',
                              download_url='http://sourceforge.net/project/showfiles.php?group_id=130831&package_id=143476',
                              package_type='Old releases',
                              platform='all platforms', platform_lower='old_releases',
                              platform_versions_supported='See the different download sections',
                              prerequisites='See the different download sections',
                              installation='See the different download sections')
                            
pages['download_old_releases'] = sep.join([download_header(), old_releases]) 

        
pages['download'] = '''        <h3>Download %(name)s</h3>
        <P>Please pick your platform on the left.
        </P>
''' 


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
       
        <P>There is a todo-list application for iPhone and iPod Touch that can synchronize with %(name)s
through the network, starting with version 0.73.2 of %(name)s. Main features are</P>

        <UL>
          <LI>Hierarchical categories.</LI>
          <LI>Editing of task subject, description, dates and completed status.</LI>
          <LI>Tap on the task's led icon to mark it complete.</LI>
          <LI>Available in English and French.</LI>
        </UL>
        </P>'''



def appendThumbnails(name):
    for filename in reversed(glob.glob(os.path.join('screenshots', '*.png'))):
        basename = os.path.basename(filename)
        release, platform, description = basename.split('-')
        platform = platform.replace('_', ' ')
        description = description[:-len('.png')].replace('_', ' ')
        caption = '%s (release %s on %s)'%(description, release, platform)
        thumbnailFilename = 'screenshots/Thumb-'+basename
        thumbnailImage = '<IMG SRC="%s" ALT="%s">'%(thumbnailFilename, caption)
        image = '<A HREF="%s">%s</A>'%(filename.replace('\\', '/'), thumbnailImage)
        pages[name] += '<P>%s<BR>%s</P>'%(caption, image)




pages['license'] = '<PRE>%s</PRE>'%meta.licenseText

pages['screenshots'] = '''<H3>Screenshots</H3>
        <P>Click on a thumbnail image to see the full size screenshot.</P>'''
appendThumbnails('screenshots')


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
        href="mailto:taskcoach-dev-subscribe@yahoogroups.com" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/join/taskcoach-dev');">taskcoach-dev-subscribe@yahoogroups.com</a></tt>
        or alternatively, if you have a Yahoo id (or don't mind creating one), 
        join via the <a href="http://groups.yahoo.com/group/taskcoach-dev/join"
        onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/join/taskcoach-dev');">webinterface</a>.</P>

        <P>To create a new translation or update an existing translation, 
        please follow these steps and guidelines:
        <OL>
            <LI>Register at <A HREF="http://launchpad.net" 
            onClick="javascript: pageTracker._trackPageview('/outgoing/launchpad.net');">Launchpad</A> and
            don't forget to set your preferred languages, i.e. the language(s)
            you want to translate to.
            <LI>Learn more about 
            <A HREF="http://translations.launchpad.net/+about" 
            onClick="javascript: pageTracker._trackPageview('/outgoing/launchpad.net/translations');">translation 
            support by Launchpad</A>.
            <LI>Go to <A HREF="https://launchpad.net/taskcoach" 
            onClick="javascript: pageTracker._trackPageview('/outgoing/launchpad.net/taskcoach');">%(name)s at 
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
            <LI>To test your translation, download it as .po file from 
            Launchpad and start %(name)s with the <TT>--po &lt;po file&gt;</TT> 
            command line option.</LI> 
        </OL>
        </P>'''

        
pages['mailinglist'] = \
'''       <H3>Mailinglist</H3>         
        <P>A Yahoo!Groups mailinglist is available for discussing
        %(name)s. You can join by sending mail to <tt><a 
        href="mailto:taskcoach-subscribe@yahoogroups.com" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/join/taskcoach-users');">taskcoach-subscribe@yahoogroups.com</a></tt>
        or alternatively, if you have a Yahoo id (or don't mind creating
        one), join via the <a
        href="http://groups.yahoo.com/group/taskcoach/join" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/join/taskcoach-users');">webinterface</a>.</P>
        <P>You can browse the <a
        href="http://groups.yahoo.com/group/taskcoach/messages" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/archive/taskcoach-users');">archive
        of messages</a> without subscribing to the mailinglist.</P>
        <p>The mailinglist is also available as the newsgroup 
        <a href="http://dir.gmane.org/gmane.comp.sysutils.pim.taskcoach" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/gmane.org/taskcoach');">gmane.comp.sysutils.pim.taskcoach</a>
        on <a href="http://gmane.org" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/gmane.org');">Gmane</a>.</p>
'''
        

pages['faq'] = \
'''    <H3>Frequently asked questions</H3>
    <P><I>I upgraded to a new version and now I cannot load my %(name)s file. It
    says: "Error loading &lt;myfile&gt;.tsk. Are you sure it is a %(name)s file?".
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
    run taskcoach.py with the same python version, %(name)s should run. So 
    if taskcoachlib is in /usr/lib/python2.X/site-packages and taskcoach.py is
    located in /usr/bin then 'python2.X /usr/bin/taskcoach.py' should work. To
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
    <P><I>Can I run %(name)s from a USB stick?</I></P>
    <P>Yes, just install it on a USB stick. In addition, in the files tab of
    the preferences dialog ('Edit' -> 'Preferences'), check 'Save settings 
    (TaskCoach.ini) in the same directory as the program' to make sure your
    settings are saved on the USB stick.</P>
    <P><I>Can I have a global hotkey to enter new tasks?</I></P>
    <P>On Windows, install <A HREF="http://www.autohotkey.com">AutoHotkey</A> 
    (it's open source and free) and put this in your <TT>AutoHotKey.ahk</TT>
    script:
    <PRE>^!n::
IfWinExist Task Coach
{
    WinActivate Task Coach
}
else
{
    Run %%A_ProgramFiles%%\\TaskCoach\\taskcoach.exe
}
WinWaitActive Task Coach
WinMenuSelectItem Task Coach,, Task, New task...
return
</PRE>
    This will register Control-Alt-N as global hotkey for entering a new
    task. %(name)s will be started if necessary. If you use a translation, you
    need to change 'Task, New task...' into your language.</P>
    <P>We'd appreciate suggestions for other platforms...</P> 
'''

pages['devinfo'] = \
'''    <h3>Information for developers</h3>
    <p>Here's some information for developers that either want to hack
    on %(name)s or reuse code.</p>
    
    <h4>Project hosting</h4>
    <P>%(name)s source code, file downloads and bug/patch/support trackers are hosted at 
    <a href="https://sourceforge.net/projects/taskcoach/"
       onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/taskcoach');" 
       title="%(name)s @ Sourceforge">Sourceforge</a>. Translations are hosted
    at 
    <a href="http://launchpad.net/taskcoach/"
       onClick="javascript: pageTracker._trackPageview('/outgoing/launchpad.net/taskcoach');"
       title="%(name)s @Launchpad">Launchpad</a>. Feature requests are hosted at
    <a href="http://taskcoach.uservoice.com/"
       onClick="javascript: pageTracker._trackPageview('/outgoing/uservoice.com');">Uservoice</a>.
    </P>
    
    <h4>Mailinglist</h4>
    <P>A Yahoo!Groups mailinglist is available for discussing the development
    of %(name)s. You can join by sending mail to <tt><a 
    href="mailto:taskcoach-dev-subscribe@yahoogroups.com"
    onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/join/taskcoach-dev');">taskcoach-dev-subscribe@yahoogroups.com</a></tt>
    or alternatively, if you have a Yahoo id (or don't mind creating one), 
    join via the <a href="http://groups.yahoo.com/group/taskcoach-dev/join"
    onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/join/taskcoach-dev');">webinterface</a>.</P>
    <P>You can browse the <a href="http://groups.yahoo.com/group/taskcoach-dev/messages"
    onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/archive/taskcoach-dev');">archive
    of messages</a> without subscribing to the mailinglist.</P>
    <p>The mailinglist is also available as the newsgroup 
    <a href="http://dir.gmane.org/gmane.comp.sysutils.pim.taskcoach.devel"
    onClick="javascript: pageTracker._trackPageview('/outgoing/gmane.org/taskcoach-dev');">gmane.comp.sysutils.pim.taskcoach.devel</a>
    on <a href="http://gmane.org"
    onClick="javascript: pageTracker._trackPageview('/outgoing/gmane.org');">Gmane</a>.</p>
    <P>A Sourceforge mailinglist is available for receiving commit messages.
    If you are a %(name)s developer you can <a href="http://lists.sourceforge.net/lists/listinfo/taskcoach-commits"
    onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/join/taskcoach-commits');">join this mailinglist</a>.
    
    <h4>Dependencies</h4>
    <p>%(name)s is developed in <A HREF="http://www.python.org"
    onClick="javascript: pageTracker._trackPageview('/outgoing/python.org');">Python</A>,
    using <A HREF="http://www.wxpython.org" 
    onClick="javascript: pageTracker._trackPageview('/outgoing/wxpython.org');">wxPython</A> for the
    graphical user interface. On Windows, 
    <A HREF="http://sourceforge.net/projects/pywin32/"
    onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/pywin32');">Pywin32</A> 
    is used as well. For generating the API documentation you need to have
    <A HREF="http://epydoc.sourceforge.net/"
    onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/epydoc');">Epydoc</A> installed. For
    generating inheritance diagrams you need to have <A
    HREF="http://www.graphviz.org"
    onClick="javascript: pageTracker._trackPageview('/outgoing/graphviz.org');">Graphviz</A> installed.</p>
    <p>The few other libraries (other than those
    provided by Python, wxPython and Pywin32) that are used are put into the
    taskcoachlib/thirdparty package and included in the source code
    repository.</p>
    
    <h4>Development environment</h4>
    <p>
    You are free to use whatever IDE you want. To make use of the Makefile you
    need to have <tt>make</tt> installed. It is installed on Linux and Mac OS X 
    by default. On Windows we recommend you to install
    <A HREF="http://www.cygwin.com"
    onClick="javascript: pageTracker._trackPageview('/outgoing/cygwin.com');">Cygwin</A> 
    which provides a shell (bash) and a whole range of useful utilities. 
    Make sure to explicitly include <tt>make</tt> in the Cygwin setup program 
    because the standard install doesn't contain <tt>make</tt>.</p>
    
    <h4>Getting the source</h4>
    <p>%(name)s source code is hosted in a <A
    HREF="http://sourceforge.net/svn/?group_id=130831"
    onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/svn');">Subversion repository 
    at SourceForge</A>. You can check out the code from the repository 
    directly or <A HREF="http://taskcoach.svn.sourceforge.net/" 
    onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/svn');">browse the
    repository</A>. Please read the file <tt>HACKING.txt</tt> after checking
    out the sources. You can generate documentation with Epydoc and Graphviz
    from the Makefile: <tt>make dot epydoc</tt>.</p>
    
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
    and driven from the Makefile (<tt>dmg</tt> target).</p>
    <h5>Linux</h5>
    <p>We create RPM and Debian packages on Ubuntu (<tt>rpm</tt> and <tt>deb</tt>
    targets) and a Fedora RPM package on Fedora (<tt>fedora</tt> target). 
    Alternatively, Linux users that have installed python and wxPython
    themselves (if not installed by default) can also use the source
    distribution. The source distributions are created by the
    <tt>sdist</tt> Makefile target.</p>
    
    <h4>Coding style</h4>
    <p>Class names are StudlyCaps. Method names are camelCase, except
    for wxPython methods that are called or overridden because those are
    StudlyCaps. At first this looked ugly, a mixture of two
    styles. But it turned out to be quite handy, since you can easily
    see whether some method is a wxPython method or not.</p>
    
    <h4>SVN usage conventions</h4>
    <p>Releases are tagged ReleaseX_Y_Z (where X has always been 0 so far) 
    and for each ReleaseX_Y_0 a branch (ReleaseX_Y_Branch) is created to
    facilitate bug fix releases. The release tagging and branching is part of 
    the release process as documented in release.py.</p>
    <p>For new big features, feature-specific branches are created to 
    facilitate parallel development, checking in changes while developing, 
    and keep the code on the main trunk releaseable. The process is as 
    follows:</p>
    <ul>
    <li>The feature is discussed on taskcoach-dev.</li>
    <li>If all agree it's a good feature to work on, a
    Feature_&lt;FeatureName&gt;_Branch branch is created and used for
    development of the feature.</li>
    <li>When the feature is done, it is announced on taskcoach-dev.</li>
    <li>The feature is tested on all platforms.</li>
    <li>The changes are merged back to main trunk.</li>
    </ul>
    <p>
    For small new features, development is done on the trunk, but all unittests
    should succeed before committing.
    </p>
    <h4>Blog</h4>
    <p>Frank keeps a not very frequent 
    <a href="http://taskcoach.blogspot.com"
    onClick="javascript: pageTracker._trackPageview('/outgoing/blogspot.com/taskcoach');">blog</a> about
    lessons learned from developing %(name)s.</p>
'''


def ensureFolderExists(folder):    
    if not os.path.exists(folder):
        os.mkdir(folder)

def writeFile(folder, filename, contents):
    ensureFolderExists(folder)
    filename = os.path.join(folder, filename)
    print 'Creating %s'%filename
    fd = file(filename, 'w')
    fd.write(contents.encode('UTF-8'))
    fd.close()
    
def expandPatterns(*patterns):
    for pattern in patterns:
        for filename in glob.glob(pattern):
            yield filename
    
def copyFiles(folder, *patterns):
    ensureFolderExists(folder)
    for source in expandPatterns(*patterns):
        target = os.path.join(folder, os.path.basename(source))
        print 'Copying %s to %s'%(source, target)
        shutil.copyfile(source, target)

def copyDir(targetFolder, subFolder, files='*'):
    targetFolder = os.path.join(targetFolder, subFolder)
    files = os.path.join(subFolder, files)
    copyFiles(targetFolder, files)

def createPAD(folder, filename='pad.xml'):
    padTemplate = file(filename).read()
    writeFile(folder, filename, padTemplate%meta.metaDict)

def createVersionFile(folder, filename='version.txt'):
    textTemplate = file(filename).read()
    writeFile(folder, filename, textTemplate%meta.metaDict)
    
def createHTMLPages(targetFolder, pages):    
    for title, text in pages.items():
        footer = style.footer
        contents = style.header + text%meta.metaDict + footer
        writeFile(targetFolder, '%s.html'%title, contents)

def createThumbnail(srcFilename, targetFolder, bitmapType=wx.BITMAP_TYPE_PNG,
                    thumbnailWidth=200.):
    if os.path.basename(srcFilename).startswith('Thumb'):
        return
    image = wx.Image(srcFilename, bitmapType)
    scaleFactor = thumbnailWidth / image.Width
    thumbnailHeight = int(image.Height * scaleFactor)
    image.Rescale(thumbnailWidth, thumbnailHeight)
    thumbFilename = os.path.join(targetFolder, 
                                 'Thumb-' + os.path.basename(srcFilename))
    print 'Creating %s'%thumbFilename
    image.SaveFile(thumbFilename, bitmapType)

def createThumbnails(targetFolder):
    for source in expandPatterns(os.path.join(targetFolder, '*.png')):
        createThumbnail(source, targetFolder)
    

websiteFolder = os.path.join('..', 'website.out')            
createHTMLPages(websiteFolder, pages)
createPAD(websiteFolder)
createVersionFile(websiteFolder)
copyFiles(websiteFolder, 'robots.txt', '*.ico', '*.css')
for subFolder in 'screenshots', 'images':
    copyDir(websiteFolder, subFolder)
createThumbnails(os.path.join(websiteFolder, 'screenshots'))
