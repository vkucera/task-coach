#!/usr/bin/env python
# -*- encoding: ISO-8859-1 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
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
        <a href="https://sourceforge.net/tracker/?group_id=130831&atid=719137"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/tracker/request_feature');">please 
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
        <P>Enjoy, <a href="mailto:%(author_email)s">%(author)s</a></P>
        '''

pages['index_fr'] = \
u'''        <P><IMG SRC="banner.png" ALT="Bandeau"></P>
        <P>%(name)s est un simple logiciel libre de gestion de listes de tâches.
        Il est né de la frustration de Frank au vu du fait que des gestionnaires
        populaires, comme ceux proposés par Outlook ou Lotus Notes, n'offrent aucune
        fonctionnalité de tâches hiérarchisées. Souvent, les tâches sont composées
        de plusieurs sous-parties. %(name)s est conçu pour gérer les tâches
        hiérarchisées.</P>

        <P>%(name)s est développé par Frank Niessink et Jérôme Laheurte, avec
        l'aide de plusieurs personnes pour les traductions. La version courante
        est la %(version)s. Beaucoup de gens l'utilisent quotidiennement, mais
        il y a encore beaucoup de fonctionnalités manquantes. S'il y a quelque chose
        que vous voudriez voir inclu, 
        <a href="https://sourceforge.net/tracker/?group_id=130831&atid=719137"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/tracker/request_feature');">veuillez 
        nous le faire savoir</a>.</P>

        <P>%(name)s est distribué sous la licence <A HREF="license.html">%(license)s</A>
        et libre d'utilisation à la fois par les particuliers et les sociétés. Si %(name)s
        vous est utile, veuillez prendre en considération la possibilité de supporter son
        développement. Pour ce faire, vous pouvez en parler autour de vous, <A HREF="i18n.html">aider
        à la traduction</A> dans votre langue, <A HREF="devinfo.html">aider à développer</A>
        de nouvelles fonctionnalités et/ou <A HREF="donations.html">faire un don</A> (pour
        aider à couvrir les coûts; tout montant est le bienvenu).</P>

        <P>%(name)s est développé à l'aide de nombreux outils; voir les références à gauche.</P>

        <P><a href="mailto:%(author_email)s">%(author)s</a></P>
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

pages['donations_fr'] = \
u'''        <H3>Dons</H3>
        <P>Les dons pout le développement de %(name)s sont appréciés. Les possibilités sont
        les suivantes:
        <UL>
            <LI><A HREF="https://sourceforge.net/donate/index.php?group_id=130831" onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/donate');">Dons
            via SourceForge</A>. Les frais sont déduits pour PayPal et 
            SourceForge. Cela vous vaudra d'être <A
        HREF="https://sourceforge.net/project/project_donations.php?group_id=130831" onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/donaters');">listé</A> en tant que donateur.
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

try:
    md5 = '<P>The MD5 digests for the files are as follows:' + \
        file('md5digests.html').read() + '</P>'
except IOError:
    md5 = ''

prerequisites = '''<a href="http://www.python.org/download/" 
onClick="javascript: pageTracker._trackPageview('/outgoing/python.org/download');">Python</a> 
<strong>%(pythonversion)s</strong> 
and <a href="http://www.wxpython.org/download.php" 
onClick="javascript: pageTracker._trackPageview('/outgoing/wxpython.org/download');">wxPython</a>
<strong>%(wxpythonversion)s</strong> (or newer).'''

prerequisites_fr = '''<a href="http://www.python.org/download/" 
onClick="javascript: pageTracker._trackPageview('/outgoing/python.org/download');">Python</a> 
<strong>%(pythonversion)s</strong> 
et <a href="http://www.wxpython.org/download.php" 
onClick="javascript: pageTracker._trackPageview('/outgoing/wxpython.org/download');">wxPython</a>
<strong>%(wxpythonversion)s</strong> (ou plus récente).'''

pages['download'] = \
'''        <H3>Download %(name)s (release %(version)s)</H3>
        <p><b>A word of warning:</b> %(name)s is currently alpha-state software. 
        This means that %(name)s contains bugs. We do our best to prevent 
        bugs and fix them as soon as possible. Still, we strongly advise you 
        to make backups of your work on a regular basis, and especially before 
        upgrading.</p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=4 valign=top><img src="windows.png" alt="Windows"></td>
        <td><b><a
        href="%(dist_download_prefix)s/%(filename)s-%(version)s-win32.exe" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/windows');">Installer</a> for Microsoft Windows</b></td></tr>
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
        <td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s.dmg"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/macosx');">Disk image (dmg)</a> for Mac OS X</b></td></tr>
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
        <td><b><a href="%(dist_download_prefix)s/%(filename_lower)s_%(version)s-1_all.deb"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/debian');">Debian package (deb)</a> for Debian</b></td></tr>
        <tr><td>Prerequisites: ''' + prerequisites + ''' If your Debian 
        installation does not have the minimally required wxPython version you 
        will need to install it yourself following 
        <a href="http://wiki.wxpython.org/InstallingOnUbuntuOrDebian">these instructions</a>.</td></tr>
        <tr><td>Installation:
        double click the package to start the installer.</td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=5 valign=top><img src="ubuntu.png" alt="Ubuntu"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename_lower)s_%(version)s-1_all.deb"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/ubuntu');">Debian package (deb)</a> for Ubuntu</b></td></tr>
        <tr><td>Prerequisites: ''' + prerequisites + ''' If your Ubuntu 
        installation does not have the minimally required wxPython version you 
        will need to install it yourself following 
        <a href="http://wiki.wxpython.org/InstallingOnUbuntuOrDebian">these instructions</a>.</td></tr>
        <tr><td>Installation:
        double click the package to start the installer.</td></tr> 
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=5 valign=top><img src="gentoo.png" alt="Gentoo"></td>
        <td><b><a href="http://packages.gentoo.org/package/app-office/taskcoach"
        onClick="javascript: pageTracker._trackPageview('/outgoing/gentoo.org/download/gentoo');">Ebuild</a> for Gentoo</b></td></tr>
        <tr><td>Installation:
        %(name)s is included in Gentoo Portage. Install with emerge:<br>
        <tt>$ emerge taskcoach</tt><td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=6 valign=top><img src="fedora.png" alt="Fedora"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename_lower)s-%(version)s-1.fc8.noarch.rpm"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/fedora');">RPM package</a> for Fedora 8-10</b></td></tr>
        <tr><td><b><a href="%(dist_download_prefix)s/%(filename_lower)s-%(version)s-1.fc11.noarch.rpm"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/fedora');">RPM package</a> for Fedora 11</b></td></tr>
        <tr><td>Prerequisites: ''' + prerequisites + '''</td></tr>
        <tr><td>Installation: <tt>$ sudo yum install --nogpgcheck %(filename_lower)s-%(version)s-1.fc*.noarch.rpm</tt></td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=5 valign=top><img src="linux.png" alt="Linux"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s-1.noarch.rpm"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/rpm');">RPM package</a> for RPM-based Linux distributions</b></td></tr>
        <tr><td>Prerequisites: ''' + prerequisites + '''</td></tr>
        <tr><td>Installation: use your package manager to install the 
        package</td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=6 valign=top><img src="source.png" alt="Source code"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s-1.src.rpm"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/source_rpm');">Source RPM package</a></b></td></tr>
        <tr><td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s.zip"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/source_zip');">Source zip archive</a></b></td></tr>
        <tr><td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s.tar.gz"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/source_gz');">Source tar archive</a></b></td></tr>
        <tr><td>Prerequisites: ''' + prerequisites + '''</td></tr>
        <tr><td>Installation: decompress the archive and run <tt>python 
        setup.py install</tt>. If you have a previous version of %(name)s 
        installed, you may need to force old files to be overwritten: 
        <tt>python setup.py install --force</tt>.</td></tr>
        </table>
        </p>
        <h3>Download daily builds</h3>
        <p>These packages are automatically generated by our <a
        href="http://www.fraca7.net:8010/waterfall">buildbot</a> each
        time a change is checked in the source tree. This is bleeding
        edge, use at your own risks.</p>
        <p>There are two sets of packages: from Trunk and from the latest Release branch. If you don't
        know what that means, you probably shouldn't download these.</p>
        <a href="http://www.fraca7.net/TaskCoach-packages/latest.py">Download page</a>
        <h3>Download previous releases of %(name)s</h3>
        <P>Download previous releases of %(name)s from 
        <A HREF="http://sourceforge.net/project/showfiles.php?group_id=130831&package_id=143476"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/old_releases');">Sourceforge</A>.
        </P>
        <h3>MD5 Digests</h3>
''' + md5 

# WTF: u'''some string''' does not produce an unicode string ?

pages['download_fr'] = \
unicode('''        <H3>Télécharger %(name)s (version %(version)s)</H3>
        <p><b>Avertissement:</b> %(name)s est actuellement au stade alpha.
        Ceci signifie que %(name)s contient des bogues. Nous faisons de notre mieux
        pour les éviter et les corriger aussitôt que possible. Cependant, nous
        vous conseillons fortement d'effectuer des copies de sauvegarde
        régulièrement, et tout spécialement avant une mise à jour.</p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=4 valign=top><img src="windows.png" alt="Windows"></td>
        <td><b><a
        href="%(dist_download_prefix)s/%(filename)s-%(version)s-win32.exe" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/windows');">Installeur</a> pour Microsoft Windows</b></td></tr>
        <tr><td>Versions de Windows supportées: Windows 2000, XP, Vista</td></tr>
        <tr><td>Prérequis: aucun.</td></tr>
        <tr><td>Installation: lancer l'installeur; il vous guidera à travers les processus
        d'installation.</td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=4 valign=top><img src="mac.png" alt="Mac OS X"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s.dmg"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/macosx');">Image disque (dmg)</a> pour Mac OS X</b></td></tr>
        <tr><td>Versions de Mac OS X supportées: Mac OS X Tiger/10.4 
        (Universal).</td></tr>
        <tr><td>Prérequis: aucun.</td></tr>
        <tr><td>Installation: Double-cliquez sur l'image et glissez l'application %(name)s
        dans votre répertoire Applications.</td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=5 valign=top><img src="debian.png" alt="Debian"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename_lower)s_%(version)s-1_all.deb"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/debian');">Paquet Debian (deb)</a> pour Debian</b></td></tr>
        <tr><td>Prérequis: ''' + prerequisites_fr + ''' Si votre installation Debian
        n'a pas la version minimale requise de wxPython, vous devrez l'installer vous-même
        en suivant
        <a href="http://wiki.wxpython.org/InstallingOnUbuntuOrDebian">ces instructions</a>.</td></tr>
        <tr><td>Installation:
        double-cliquez sur le paquet pour démarrer l'installeur.</td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=5 valign=top><img src="ubuntu.png" alt="Ubuntu"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename_lower)s_%(version)s-1_all.deb"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/ubuntu');">Paquet Debian (deb)</a> pour Ubuntu</b></td></tr>
        <tr><td>Prérequis: ''' + prerequisites_fr + ''' Si votre installation Ubuntu 
        n'a pas la version minimale requise de wxPython, vous devrez l'installer vous-même
        en suivant
        <a href="http://wiki.wxpython.org/InstallingOnUbuntuOrDebian">ces instructions</a>.</td></tr>
        <tr><td>Installation:
        double-cliquez sur le paquet pour démarrer l'installeur.</td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=5 valign=top><img src="gentoo.png" alt="Gentoo"></td>
        <td><b><a href="http://packages.gentoo.org/package/app-office/taskcoach"
        onClick="javascript: pageTracker._trackPageview('/outgoing/gentoo.org/download/gentoo');">Ebuild</a> pour Gentoo</b></td></tr>
        <tr><td>Installation:
        %(name)s est inclu dans Gentoo Portage. Installation avec emerge:<br>
        <tt>$ emerge taskcoach</tt><td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=6 valign=top><img src="fedora.png" alt="Fedora"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename_lower)s-%(version)s-1.fc8.noarch.rpm"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/fedora');">Paquet RPM</a> pour Fedora 8-10</b></td></tr>
        <tr><td><b><a href="%(dist_download_prefix)s/%(filename_lower)s-%(version)s-1.fc11.noarch.rpm"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/fedora');">Paquet RPM</a> pour Fedora 11</b></td></tr>
        <tr><td>Prérequis: ''' + prerequisites_fr + '''</td></tr>
        <tr><td>Installation: <tt>$ sudo yum install --nogpgcheck %(filename_lower)s-%(version)s-1.fc*.noarch.rpm</tt></td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=5 valign=top><img src="linux.png" alt="Linux"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s-1.noarch.rpm"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/rpm');">Paquet RPM</a> pour les distributions Linux basées sur RPM</b></td></tr>
        <tr><td>Prérequis: ''' + prerequisites_fr + '''</td></tr>
        <tr><td>Installation: utilisez votre gestionnaire de paquets habituel pour installer le paquet.</td></tr>
        </table>
        </p>
        <hr>
        <p>
        <table>
        <tr><td rowspan=6 valign=top><img src="source.png" alt="Code source"></td>
        <td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s-1.src.rpm"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/source_rpm');">Paquet RPM source</a></b></td></tr>
        <tr><td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s.zip"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/source_zip');">Archive zip des sources</a></b></td></tr>
        <tr><td><b><a href="%(dist_download_prefix)s/%(filename)s-%(version)s.tar.gz"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/source_gz');">Archive tar des sources</a></b></td></tr>
        <tr><td>Prérequis: ''' + prerequisites_fr + '''</td></tr>
        <tr><td>Installation: Décompressez l'archive et lancez <tt>python 
        setup.py install</tt>. Si vous avez une version de %(name)s déjà installée,
        il se peut que vouz ayez à forcer l'écrasement des vieux fichiers:
        <tt>python setup.py install --force</tt>.</td></tr>
        </table>
        </p>
        <h3>Télécharger les versions plus anciennes de %(name)s</h3>
        <P>Télécharger les versions précédentes de %(name)s depuis 
        <A HREF="http://sourceforge.net/project/showfiles.php?group_id=130831&package_id=143476"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/download/old_releases');">Sourceforge</A>.
        </P>
        <h3>Sommes MD5</h3>
''', 'ISO-8859-1') + md5

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
        See the list of <A HREF="https://sourceforge.net/tracker/?group_id=130831&atid=719137"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/tracker/feature_requests');">requested features</A> 
        for features that people miss.
        </P>'''

pages['features_fr'] = \
unicode('''        <H3>Fonctionnalités</H3>
        <P>%(name)s a, à l'heure actuelle (%(version)s), les fonctionnalités suivantes:
        <UL>
            <LI>Création, édition et suppression de tâches et de sous-tâches.
            <LI>Les tâches ont un sujet, une description, une priorité, une date de
            départ, une date dûe, une date de fin et un rappel optionel. Elles
            peuvent être récurrentes sur une base quotidienne, hebdomadaire ou
            mensuelle.
            <LI>Les tâches peuvent être visualisées sous forme de liste ou d'arborescence.
            <LI>Les tâches peuvent être triées sur la base de leurs attributs, par exemple
            sujet, budget, budget restant, date dûe, etc.
            <LI>Plusieurs filtres pour, par exemple, cacher les tâches terminées ou voir
            uniquement les tâches dûes aujourd'hui.
            <LI>Une tâche peut être créée en glissant/déposant un courriel depuis
            Outlook ou Thunderbird sur la vue.
            <LI>Des pièces jointes peuvent être associées aux tâches, notes et catégories
            en glissant/déposant des fichiers, courriels depuis Outlook ou Thunderbird,
            ou des URLs sur une tâche, note ou catégorie.
            <LI>L'état d'une tâche dépend de ceux de ses sous-tâches et réciproquement.
            Par exemple, si vous marquez terminée la dernière sous-tâche non terminée d'une
            tâche, celle-ci sera automatiquement marquée terminée aussi.
            <LI>Les tâches et les notes peuvent être associées à des catégories définies
            par l'utilisateur.
            <LI>Les réglages sont persistents et sauvegardés automatiquement. Le dernier
            fichier ouvert est chargé automatiquement au démarrage de %(name)s.
            <LI>Suivi du temps passé sur les tâches. Les tâches peuvent avoir un budget.
            Le temps passé peut être visualisé par période d'activité individuelle, par
            jour, semaine ou mois.
            <LI>Le format des fichiers %(name)s est XML.
            <LI>Les tâches, notes, périodes d'activité et catégories peuvent être exportées
            aux formats HTML et CSV (champs séparés par une virgule). Les périodes d'activité
            peuvent être exportées au format iCalendar/ICS.
            <LI>Les tâches, notes, périodes d'activité et catégories peuvent être imprimées.
            %(name)s imprime les informations visibles dans le vue courante, en tenant compte
            des filtres et critères de tri.
            <LI>%(name)s peut être exécuté depuis un périphérique de stockage amovible.
            <LI>Les tâches et notes peuvent être synchronisées vers un serveur
            <a href="http://www.funambol.com/">Funambol</a> comme
            <a href="http://www.scheduleworld.com">ScheduleWorld</a>.
        </UL>
        <H3>Fonctionnalités manquantes</H3>
        <P>
        Vous pouvez en consulter la liste des <A HREF="https://sourceforge.net/tracker/?group_id=130831&atid=719137"
        onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/tracker/feature_requests');">fonctionnalités demandées</A> 
        par des utilisateurs.
        </P>''', 'ISO-8859-1')


def appendThumbnails(name, flt):
    for filename in reversed(glob.glob(os.path.join('screenshots', '*.png'))):
        if flt(filename):
            basename = os.path.basename(filename)
            release, platform, description = basename.split('-')
            platform = platform.replace('_', ' ')
            description = description[:-len('.png')].replace('_', ' ')
            caption = '%s (release %s on %s)'%(description, release, platform)
            thumbnailFilename = 'screenshots/Thumb-'+basename
            thumbnailImage = '<IMG SRC="%s" ALT="%s">'%(thumbnailFilename, caption)
            image = '<A HREF="%s">%s</A>'%(filename.replace('\\', '/'), thumbnailImage)
            pages[name] += '<P>%s<BR>%s</P>'%(caption, image)
pages['iPhone'] = '''<H3>iPhone</H3>
        <P>There is a todo-list application for iPhone that can synchronize with Task Coach
through the network, starting with version 0.73.2 of Task Coach. Main features are</P>

        <UL>
          <LI>Hierarchical categories.</LI>
          <LI>Editing of task subject, description, dates and completed status.</LI>
          <LI>Tap on the task's led icon to mark it complete.</LI>
          <LI>Available in English and French.</LI>
        </UL>

        <P>It is available on the <a href="http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewSoftware?id=311403563&mt=8">AppStore.</a></P>

        <P>More features are planned, like support for multiple task files and effort tracking.
Here are some thumbnails of the UI:</P>'''
appendThumbnails('iPhone', lambda x: x.find('iPhone') != -1)

pages['license'] = '<PRE>%s</PRE>'%meta.licenseText

pages['screenshots'] = '''<H3>Screenshots</H3>
        <P>Click on a thumbnail image to see the full size screenshot.</P>'''
appendThumbnails('screenshots', lambda x: x.find('iPhone') == -1)

pages['screenshots_fr'] = unicode('''<H3>Captures d'écran</H3>
        <P>Cliquez sur la prévisualisation pour voir la capture en taille réelle.</P>''', 'ISO-8859-1')
appendThumbnails('screenshots_fr', lambda x: x.find('iPhone') == -1)


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
        </OL>
        </P>'''

pages['i18n_fr'] = \
unicode('''        <H3>Internationalisation</H3>
        <H4>Informations pour les utilisateurs</H4>
        <P>A l'heure actuelle, %(name)s est disponible dans un certain nombre de langues: '''\
        + ', '.join(sorted(meta.languages.keys())) + \
        '''. Vous pouvez sélectionner la langue via le menu 'Editer' -> 
        'Préférences'. Cliquez sur l'icône 'Langage', sélectionnez la langue
        de votre choix et redémarrez %(name)s.
        <H4>Instructions pour les traducteurs</H4>
        <P>Les traductions dans d'autres langues sont les bienvenues.
        Ayez conscience que, en plus de fournir la traduction initiale,
        il sera attendu que vous mainteniez cette traduction à jour au
        fur et à mesure des nouvelles versions de %(name)s.</P>
        <P>Une chaîne de courriels Yahoo!Groups est disponible pour les discussions
        sur le développement et la traduction de %(name)s. Vous pouvez vous y joindre
        en envoyant un courriel à <tt><a 
        href="mailto:taskcoach-dev-subscribe@yahoogroups.com" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/join/taskcoach-dev');">taskcoach-dev-subscribe@yahoogroups.com</a></tt>
        ou bien, si vous disposez d'un identifiant Yahoo (ou en créez un), via l'<a href="http://groups.yahoo.com/group/taskcoach-dev/join"
        onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/join/taskcoach-dev');">interface Web</a>. Veuillez noter que cette chaîne est en anglais; un message en français ou en néerlandais aura néanmoins une réponse de l'un des deux développeurs.</P>

        <P>Pour créer une nouvelle traduction ou mettre à jour une traduction existante,
        veuillez suivre les consignes suivantes:
        <OL>
            <LI>Enregistrez-vous sur <A HREF="http://launchpad.net" 
            onClick="javascript: pageTracker._trackPageview('/outgoing/launchpad.net');">Launchpad</A> et
            n'oubliez pas de spécifier votre langage préféré, c.à.d le langage cible de votre
            traduction.
            <LI>Plus d'informations sur 
            <A HREF="http://translations.launchpad.net/+about" 
            onClick="javascript: pageTracker._trackPageview('/outgoing/launchpad.net/translations');">les 
            traductions sur Launchpad</A>.
            <LI>Allez sur <A HREF="https://launchpad.net/taskcoach" 
            onClick="javascript: pageTracker._trackPageview('/outgoing/launchpad.net/taskcoach');">%(name)s sur 
            Launchpad</A> et cliquez sur "Help translate".
            <LI>Créez une nouvelle traduction ou commencez à mettre à jour une traduction existante.
            <LI>Assurez-vous de bien comprendre comment
            <A HREF="http://docs.python.org/lib/typesseq-strings.html">le système de
            formatage de chaînes Python</A> fonctionne car %(name)s utilise à la fois
            la variante de type '%%s' et la variante '%%(clef)s'. Si le formatage
            est utilisé dans la version anglaise d'une chaîne, la même formatage doit apparaître
            dans la chaîne traduite. De plus, les spécifications de type '%%s' doivent
            apparaître dans le même ordre dans les deux chaînes. Les formats de type
            '%%(clef)s' peuvent apparaître dans un ordre différent.
            <LI>Ne traduisez pas les clef de format; si vous voyez '%%(name)s', ne
            traduisez pas 'name'.
            <LI>Ne traduisez pas les raccourcis clavier; si vous voyez 'Shift+Ctrl+V',
            ne traduisez pas 'Shift' et 'Ctrl', même si votre clavier utilise des
            libellés différents pour ces deux touches. Utiliser une lettre différente est
            permis, mais assurez-vous que chaque lettre n'est utilisée qu'une fois.</LI>
        </OL>
        </P>''', 'ISO-8859-1')
        
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
        
pages['mailinglist_fr'] = \
unicode('''       <H3>Chaîne de courriel</H3>         
        <P>Une chaîne de courriel Yahoo!Groups est disponible pour discuter de %(name)s.
        Vous pouvez vous y joindre en envoyant un courriel à <tt><a
        href="mailto:taskcoach-subscribe@yahoogroups.com" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/join/taskcoach-users');">taskcoach-subscribe@yahoogroups.com</a></tt>
        ou, si vous disposez d'un identifiant Yahoo! (ou en créez un), via l'<a
        href="http://groups.yahoo.com/group/taskcoach/join" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/join/taskcoach-users');">interface Web</a>. Veuillez noter que cette chaîne est en anglais; un message en français ou en néerlandais aura néanmoins une réponse de l'un des deux développeurs.</P>
        <P>Vous pouvez parcourir les <a
        href="http://groups.yahoo.com/group/taskcoach/messages" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/archive/taskcoach-users');">archives
        des messages</a> sans vous inscrire à la liste.</P>
        <p>La liste est aussi accessible sur Usenet via le groupe
        <a href="http://dir.gmane.org/gmane.comp.sysutils.pim.taskcoach" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/gmane.org/taskcoach');">gmane.comp.sysutils.pim.taskcoach</a>
        sur <a href="http://gmane.org" 
        onClick="javascript: pageTracker._trackPageview('/outgoing/gmane.org');">Gmane</a>.</p>
''', 'ISO-8859-1')

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
    <P><I>Can I run Task Coach from a USB stick?</I></P>
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

pages['faq_fr'] = \
unicode('''    <H3>Questions fréquentes (FAQ)</H3>
    <P><I>J'ai mis à jour et je ne peux plus ouvrir mon fichier %(name)s. Le message
    d'erreur est: "Erreur lors du chargement de &ltfichier&gt.tsk. Etes-vous sûr que
    c'est un fichier %(name)s ? Je suis certain que le fichier est valide. Que puis-je faire ?</I></P>
    <P>Supprimez votre fichier TaskCoach.ini et réessayez. Quelquefois, une erreur au
    chargement du fichier de configuration causera un problème au chargement de fichiers
    .tsk valides. Le fichier TaskCoach.ini est situé dans le répertoire C:\Documents and
    Settings\&lt;votre nom&gt;\Application Data\TaskCoach si vous êtes sous Windows et dans
    /home/&lt;votre nom&gt;/.TaskCoach si vous êtes sous Linux.</P>
    <P><I>Je suis sous Windows et lorsque je tente d'installer une nouvelle version de
    %(name)s, l'installeur se plaint de ne pas pouvoir remplacer le fichier MSVCP7.dll.</I></P>
    <P>Assurez-vous que l'ancienne version de %(name)s n'est pas lancée, ou une
    application lancée par %(name)s (par exemple un navigateur Web lancé en cliquant
    un lien dans %(name)s).</P>
    <P><I>Je suis sous Linux et aprés avoir lancé taskcoach.py, j'ai un message
    "ERROR: cannot import the library 'taskcoachlib' " et je suis redirigé ici.</I></P>
    <P>Cela signifie probablement que la version de Python que vous utilisez pour lancer
    taskcoach.py n'est pas celle où le répertoire taskcoachlib a été installé; Python ne
    peut donc pas le trouver. Ce répertoire est situé dans
    /usr/lib/python2.X/site-packages. Si vous le trouvez et lancez taskcoach.py avec
    la même version de Python, cela devrait fonctionner. Donc si taskcoachlib est dans
    /usr/lib/python2.X/site-packages et taskcoach.py dans
    /usr/bin alors 'python2.X /usr/bin/taskcoach.py' devrait faire l'affaire.
    Pour régler définitivement ce problème, vous pouvez déplacer le répertoire taskcoachlib
    dans le répertoire site-packages de votre version par défaut de Python. Pour
    déterminer quelle est votre version par défaut de Python, démarrez python en ligne
    de commande, vérifiez le numéro de version et sortez via Ctrl-D. Ensuite, déplacez
    le répertoire taskcoachlib comme suit (2.D est le numéro de version de votre
    Python par défaut, 2.C est le numéro de version où taskcoachlib a été installé):
    'mv /usr/lib/python2.C/site-packages/taskcoachlib 
    /usr/lib/python2.D/site-packages'. Maintenant taskcoach.py devrait fonctionner.</P> 
    <P><I>Je suis sous Linux et j'utilise un gestionnaire de fenêtres avec des
    bureaux virtuels. Lorsque je (re)viens sur le bureau sur lequel %(name)s était
    lancé, je ne le retrouve pas. Où est-il passé ?</I></P>
    <P>%(name)s est probablement minimisé. Cherchez la petite icône %(name)s
    dans la barre système, cliquez dessus avec le bouton droit et choisissez 'Restaurer'.
    Apparemment, le changement de bureau virtuel est implémenté en envoyant un
    évènement de minimalisation à toutes les applications. Malheureusement, %(name)s
    n'a aucun moyen de distinguer un tel évènement de celui généré par l'utilisateur
    minimisant la fenêtre. Si vous avez ce problème, vous devriez changer l'option
    'Cacher la fenêtre principale lors de l'icônification'; voir 'Editer' -> 'Préférences'.</P>
    <P><I>Est-ce que je peux démarrer le suivi de plus d'une tâche en même temps ?</I></P>
    <P>Oui, lorsque le suivi d'une tâche est démarré, sélectionnez-en une autre, faites
    un click droit et choisissez 'Nouvel effort...'. Si vous ne renseignez pas la fin
    de l'effort, cette seconde tâche sera suivie aussi.</P>
    <P><I>Comment puis-je marquer une tâche "inactive" ?</I></P>
    <P>Changez la date de début de la tâche en une date à venir ou ne la renseignez
    pas du tout en décochant la case à cocher à gauche de la date de début.</P>
    <P><I>Comment fonctionne le redimensionnement des colonnes ?</I></P>
    <P>Dans toutes les vues avec colonnes, la colonne Sujet est automatiquement
    redimensionnée pour prendre tout l'espace restant. Pour redimensionner une colonne,
    glissez le bord <b>droit</b> de l'en-tête de cette colonne. Si vous augmentez la
    taille de la colonne Sujet, toutes les autres diminueront de taille. Si vous la 
    diminuez, toutes seront augmentées. Si vous augmentez la taille d'une autre
    colonne, la colonne sujet diminuera et vice-versa.</P>
    <P><I>Est-ce que je peux lancer %(name)s depuis une clef USB ?</I></P>
    <P>Oui, il suffit de l'installer sur la clef USB. De plus, dans l'onglet Fichiers
    du dialogue de préférences ('Edition' -> 'Préférences'), cochez la case
    'Sauver les paramètres (TaskCoach.ini) dans le même répertoire que le programme'
    afin que vos paramètres soient sauvés sur la clef USB.</P>
    <P><I>Puis-je avoir un raccourci clavier global pour créer de nouvelles tâches ?</I></P>
    <P>Sous Windows, installez <A HREF="http://www.autohotkey.com">AutoHotkey</A> 
    (c'est un logiciel libre et gratuit) et placer le texte suivant dans votre fichier
    <tt>AutoHotKey.ahk</tt>:
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
    Ceci enregistrera Ctrl-Alt-N comme raccourci global pour créer une nouvelle tâche.
    %(name)s sera lancé si nécessaire. Si vous utilisez un autre langage que l'anglais, vous
    devrez changer 'Task, New Task...' pour se conformer à votre langue.</P>
    <P>Nous apprécierions des suggestions pour les autres systèmes d'exploitation...</P>
''', 'ISO-8859-1')

pages['devinfo'] = \
'''    <h3>Information for developers</h3>
    <p>Here's some information for developers that either want to hack
    on %(name)s or reuse code.</p>
    
    <h4>Project hosting</h4>
    <P>%(name)s source code, file downloads and trackers are hosted at 
    <a href="https://sourceforge.net/projects/taskcoach/"
       onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/taskcoach');" 
       title="%(name)s @ Sourceforge">Sourceforge</a>. Translations are hosted
    at 
    <a href="http://launchpad.net/taskcoach/"
       onClick="javascript: pageTracker._trackPageview('/outgoing/launchpad.net/taskcoach');"
       title="%(name)s @Launchpad">Launchpad</a>.
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

pages['devinfo_fr'] = \
unicode('''    <h3>Informations pour les développeurs</h3>
    <p>Voici quelques informations pour les développeurs qui voudraient
    bricoler sur %(name)s ou réutiliser du code.</p>

    <h4>Hébergement du projet</h4>
    <p>Le code source de %(name)s, l'hébergement des fichiers et des suivis sont sur
    <a href="https://sourceforge.net/projects/taskcoach/"
       onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/taskcoach');" 
       title="%(name)s @ Sourceforge">Sourceforge</a>. Les traductions sont hébergées sur
    <a href="http://launchpad.net/taskcoach/"
       onClick="javascript: pageTracker._trackPageview('/outgoing/launchpad.net/taskcoach');"
       title="%(name)s @Launchpad">Launchpad</a>.
    </P>
    
    <h4>Chaînes de courriel</h4>
    <P>Une chaîne de courriels Yahoo!Groups est disponible pour les discussions sur le
    développement de %(name)s. Vous pouvez y souscrire en envoyant un courriel à <tt><a
    href="mailto:taskcoach-dev-subscribe@yahoogroups.com"
    onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/join/taskcoach-dev');">taskcoach-dev-subscribe@yahoogroups.com</a></tt>
    ou bien, si vous disposez d'un identifiant Yahoo! (ou en créez un), via l'<a href="http://groups.yahoo.com/group/taskcoach-dev/join"
    onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/join/taskcoach-dev');">interface Web</a>.</P>
    <P>Vous pouvez parcourir les <a href="http://groups.yahoo.com/group/taskcoach-dev/messages"
    onClick="javascript: pageTracker._trackPageview('/outgoing/yahoogroups.com/archive/taskcoach-dev');">archives
    de messages</a> sans vous inscrire.</P>
    <p>La chaîne est aussi disponible sur Usenet dans le groupe 
    <a href="http://dir.gmane.org/gmane.comp.sysutils.pim.taskcoach.devel"
    onClick="javascript: pageTracker._trackPageview('/outgoing/gmane.org/taskcoach-dev');">gmane.comp.sysutils.pim.taskcoach.devel</a>
    sur <a href="http://gmane.org"
    onClick="javascript: pageTracker._trackPageview('/outgoing/gmane.org');">Gmane</a>.</p>
    <p>Une chaîne Sourceforge est aussi disponible pour recevoir les messages de commit.
    Si vous êtes un développeur %(name)s vous pouvez <a href="http://lists.sourceforge.net/lists/listinfo/taskcoach-commits"
    onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/join/taskcoach-commits');">la joindre</a></p>

    <p>Veuillez noter que les discussions se font en langue anglaise. Un message en Français ou Néerlandais recevra
    sans doute une réponse de l'un des deux développeurs, mais n'en abusez pas.</p>
    
    <h4>Dépendances</h4>
    <p>%(name)s est écrit en <A HREF="http://www.python.org"
    onClick="javascript: pageTracker._trackPageview('/outgoing/python.org');">Python</A>,
    avec <A HREF="http://www.wxpython.org" 
    onClick="javascript: pageTracker._trackPageview('/outgoing/wxpython.org');">wxPython</A> pour
    l'interface graphique. Sous Windows,
    <A HREF="http://sourceforge.net/projects/pywin32/"
    onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/pywin32');">Pywin32</A> 
    est aussi utilisé. Pour générer la documentation des API vous aurez besoin de
    <A HREF="http://epydoc.sourceforge.net/"
    onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/epydoc');">Epydoc</A>. Pour
    la génération des diagrammes d'héritage, vous aurez besoin de <a
    HREF="http://www.graphviz.org"
    onClick="javascript: pageTracker._trackPageview('/outgoing/graphviz.org');">Graphviz</A>.</p>
    <p>Les quelques autres bibliothèques (en dehors de celles fournies par Python, wxPython et Pywin32) nécessaires
    sont placées dans le package taskcoachlib/thirdparty et incluses dans le dépot des sources.</p>

    <h4>Environnement de développement</h4>
    <p>Vous êtes libre d'utiliser l'EDI que vous voulez. Pour utiliser la 
    Makefile vous aurez besoin de <tt>make</tt>. Il est installé par défaut 
    sous Linux et MacOS. Sous Windows, nous vous conseillons d'installer
    <A HREF="http://www.cygwin.com"
    onClick="javascript: pageTracker._trackPageview('/outgoing/cygwin.com');">Cygwin</A>
    qui fournit un shell (bash) et une flopée d'utilitaires. Assurez-vous 
    d'inclure explicitement <tt>make</tt> dans le programme d'installation de 
    Cygwin car l'installation standard ne l'inclut pas.</p>

    <h4>Récupérer le code source</h4>
    <p>Le code source de %(name)s est hébergé dans un <a
    HREF="http://sourceforge.net/svn/?group_id=130831"
    onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/svn');">dépôt Subversion
    sur SourceForge</a>. Vous pouvez récupérer le code depuis le dépôt directement ou bien
    <A HREF="http://taskcoach.svn.sourceforge.net/" 
    onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/svn');">parcourir
    le dépôt</A>. Vous pouvez générer la documentation avec Epydoc et Graphviz à partir
    de la Makefile: <tt> make dot epydoc</tt>.</p>

    <h4>Tests</h4>
    <p>Les tests peuvent être lancés depuis la Makefile. Il y a des cibles pour
    <tt>unittests</tt>, <tt>integrationtests</tt>,
    <tt>releasetests</tt>, et <tt>alltests</tt>. Ces cibles invoquent toutes
    le script tests/test.py. Lancez <tt>tests/test.py --help</tt> pour avoir
    une liste de toutes les options (y compris le profilage, les tests de couverture de test, etc).</p>

    <h4>Construire les distributions</h4>
    <p>La Makefile est utilisée pour construire les différentes distributions
    de %(name)s. Actuellement, un installeur Windows, une image disque MacOS, des paquets RPM
    et Debian sont créés et les sources empaquetés en archives compréssées (.zip
    et .tar.gz). La Makefile contient des cibles pour chacune de ces distributions.
    L'essentiel du code qui les construit est situé dans make.py. A son tour, make.py
    importe setup.py. Ces deux fichiers ont été séparés afin que setup.py ne contienne
    que les informations nécessaires à distutils pour <i>installer</i>, pendant que
    make.py contient toutes les informations nécessaires à la <i>construction</i> des
    distributions. Seul setup.py est inclu dans la distribution source.</p>
    <h5>Windows</h5>
    <p>Sous Windows, py2exe est utilisé pour embarquer l'application avec
    l'interpréteur Python et les bibliothèques. Innosetup est utilisé pour créer
    un installeur exécutable.
    Tout le code nécessaire est dans make.py et dirigé depuis la Makefile (cible
    <tt>windist</tt>).
    <h5>Mac OSX</h5>
    <p>Sous Mac OSX, py2app est utilisé pour construire le bundle. L'application
    résultante est placée dans un fichier dmg grâce à l'utilitaire <tt>hdiutil</tt>
    qui est installé avec Mac OSX.
    Tout le code nécessaire est dans make.py et dirigé depuis la Makefile (cible
    <tt>dmg</tt>).</p>
    <h5>Linux</h5>
    <p>Nous créons les paquets RPM et Debian sous Ubuntu (cibles <tt>rpm</tt> et <tt>deb</tt>)
    et le paquet RPM Fedora sous Fedora (cible <tt>fedora</tt>). Alternativement,
    les utilisateurs Linux qui ont installé Python et wxPython eux-même (ou si ces
    paquets sont installés par défaut) peuvent aussi utiliser la distribution source.
    Celle-ci est créée par la cible <tt>sdist</tt> de la Makefile.</p>

    <h4>Style de codage</h4>
    <p>Les noms de classe sont capitalisées (StudlyCaps). Les noms de méthodes
    sont en camelCase, à part les méthodes wxPython qui sont invoquées ou
    surchargées car celles-ci sont capitalisées. Au début ce cela laid,
    ce mélange de deux styles. Mais finalement c'est plutôt pratique, cela permet
    de distinguer facilement un méthode wxPython d'une autre.</p>

    <h4>Conventions d'utilisation de SVN</h4>
    <p>Les releases sont taggées ReleaseX_Y_Z (où X a toujours été 0 jusqu'à
    maintenant) et pour chaque ReleaseX_Y_0 une branche (ReleaseX_Y_Branch)
    est créée pour faciliter les releases de correctifs. Ceci fait partie
    du processus de release tel que documenté dans release.py.</p>
    <p>Pour les nouvelles fonctionnalités majeures, des branches spécifiques
    sont créées pour faciliter le développement parallèle et maintenir le code
    de trunk stable. Le processus est le suivant:</p>
    <ul>
    <li>La fonctionnalité est discutée sur taskcoach-dev.</li>
    <li>Si tout le monde est d'accord sur son utilité, une branche Feature_&lt;FeatureName&gt;_Branch
    est créée et utilisée pour le développement de cette fonctionnalité.</li>
    <li>Lorsqu'elle est prête, elle est annoncée sur taskcoach-dev.</li>
    <li>Elle est testée sur toutes les plate-formes.</li>
    <li>Les modifications sont fusionnées dans trunk.</li>
    </ul>
    <p>
    Pour les fonctionnalités mineures, le développement est fait dans trunk, mais
    tous les tests unitaires doivent passer avant de committer.</p>
    <h4>Blog</h4>
    <p>Frank a un <a href="http://taskcoach.blogspot.com"
    onClick="javascript: pageTracker._trackPageview('/outgoing/blogspot.com/taskcoach');">blog</a> (pas
    mis à jour trés souvent) à propos des leçons tirées du développement de %(name)s.</p>
''', 'ISO-8859-1')

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

def createPAD(folder, filename='pad.xml'):
    padTemplate = file(filename).read()
    writeFile(folder, filename, padTemplate%meta.metaDict)
    
def createHTMLPages(targetFolder, pages):    
    for title, text in pages.items():
        footer = style.footer
        if title.endswith('_fr'):
            footer = style.footer_fr
        contents = style.header + text%meta.metaDict + footer
        writeFile(targetFolder, '%s.html'%title, contents)

def createThumbnail(srcFilename, targetFolder, bitmapType=wx.BITMAP_TYPE_PNG,
                    thumbnailWidth=200.):
    image = wx.Image(srcFilename, bitmapType)
    scaleFactor = thumbnailWidth / image.Width
    thumbnailHeight = int(image.Height * scaleFactor)
    image.Rescale(thumbnailWidth, thumbnailHeight)
    thumbFilename = os.path.join(targetFolder, 
                                 'Thumb-' + os.path.basename(srcFilename))
    print 'Creating %s'%thumbFilename
    image.SaveFile(thumbFilename, bitmapType)

def createThumbnails(targetFolder, *patterns):
    for source in expandPatterns(*patterns):
        createThumbnail(source, targetFolder)

def copyScreenshots(targetFolder, screenshotFolder='screenshots', 
                                  screenshotFiles='*.png'):
    screenshotTargetFolder = os.path.join(targetFolder, screenshotFolder)
    screenshotFiles = os.path.join(screenshotFolder, screenshotFiles)
    copyFiles(screenshotTargetFolder, screenshotFiles)
    createThumbnails(screenshotTargetFolder, screenshotFiles)

websiteFolder = os.path.join('..', 'website.out')            
createHTMLPages(websiteFolder, pages)
createPAD(websiteFolder)
copyFiles(websiteFolder, '*.png', '*.ico', '*.css', '../icons.in/splash.png', '.htaccess')    
copyScreenshots(websiteFolder)
