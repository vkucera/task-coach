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

'''
Release steps:
- Get latest translations from Launchpad
- make clean all 
- make alltests 
- Run this script (phase1) to upload the distributions to Sourceforge, 
  generate MD5 digests and generate website.
- Add file releases on Sourceforge by hand.
- Run this script (phase2) to publish to Sourceforge website, Chello (my ISP) 
  and PyPI (Python Package Index).
- Post project news on Sourceforge by hand.
- Post release notification on Freshmeat by hand.
- Email taskcoach@yahoogroups.com and python-announce@python.org.
- Tag source code with tag ReleaseX_Y_Z.
- Create branch if feature release.
- Add release to Sourceforge bug tracker groups.
- Set bug reports and/or feature requests to Pending state.
'''

import ftplib, smtplib, os, glob, sys, getpass, md5, ConfigParser, \
    taskcoachlib.meta

class Settings(ConfigParser.SafeConfigParser, object):
    def __init__(self):
        super(Settings, self).__init__()
        self.setDefaults()
        self.filename = os.path.expanduser('~/.tcreleaserc')
        self.read(self.filename)

    def setDefaults(self):
        defaults = dict(sourceforge=['username', 'password'],
                        smtp=['hostname', 'port', 'username', 'password',
                              'sender_name', 'sender_email_address'],
                        chello=['hostname', 'username', 'password'],
                        pypi=['username', 'password'])
        for section in defaults:
            self.add_section(section)
            for option in defaults[section]:
                self.set(section, option, 'ask')

    def get(self, section, option):
        value = super(Settings, self).get(section, option)
        if value == 'ask':
            if option == 'password':
                get_input = getpass.getpass
            else:
                get_input = raw_input
            value = get_input('%s %s: '%(section, option)).strip()
            self.set(section, option, value)
            self.write(file(self.filename, 'w'))
        return value

def uploadDistributionsToSourceForge(settings):
    print 'Uploading distributions to SourceForge...'
    username = settings.get('sourceforge', 'username')
    os.system('rsync -avP -e ssh dist/* %s@frs.sourceforge.net:uploads/' % \
              username)
    print 'Done uploading distributions to SourceForge.'

def generateMD5Digests(settings):
    print 'Generating MD5 digests...'
    contents = '''<TABLE>
    <TR>
        <TH ALIGN='LEFT'>Filename</TH>
        <TH ALIGN='LEFT'>MD5 digest</TH>
    </TR>
'''
    for filename in glob.glob(os.path.join('dist', '*')):
        
        md5digest = md5.new(file(filename, 'rb').read())
        filename = os.path.basename(filename)
        hexdigest = md5digest.hexdigest()
        contents += '''    <TR>
        <TD>%s</TD>
        <TD>%s</TD>
    </TR>
'''%(filename, hexdigest)
        print 'MD5 digest for %s is %s'%(filename, hexdigest)
    contents += '</TABLE>\n'
    
    print 'Writing MD5 digests...'
    md5digestsFile = file(os.path.join('website.in', 'md5digests.html'), 'w')
    md5digestsFile.write(contents)
    md5digestsFile.close()
    print 'Done generating MD5 digests.'


def generateWebsite(settings):
    print 'Generating website...'
    os.chdir('website.in')
    os.system('python make.py')
    os.chdir('..')
    print 'Done generating website...'


class SimpleFTP(ftplib.FTP, object):
    def put(self, folder):
        for root, dirs, filenames in os.walk(folder):
            if root != folder:
                print 'Change into %s'%root
                self.cwd(os.path.basename(root))
            for dir in dirs:
                print 'Create %s'%os.path.join(root, dir)
                try:
                    self.mkd(dir)
                except ftplib.error_perm, info:
                    print info
            for filename in filenames:
                print 'Store %s'%os.path.join(root, filename)
                self.storbinary('STOR %s'%filename, 
                                file(os.path.join(root, filename), 'rb'))

def uploadWebsiteToChello(settings):
    hostname = settings.get('chello', 'hostname')
    username = settings.get('chello', 'username')
    password = settings.get('chello', 'password')
    
    if hostname and username and password:
        print "Uploading website to Chello..."
        chello = SimpleFTP(hostname, username, password)
        os.chdir('website.out')
        chello.put('.')
        chello.quit()
        os.chdir('..')
        print 'Done uploading website to Chello.'
    else:
        print 'Warning: cannot upload website to Chello; missing credentials'

def uploadWebsiteToSourceForge(settings):
    print 'Uploading website to SourceForge...'
    username = settings.get('sourceforge', 'username')
    os.system('scp -r website.out/* %s@web.sourceforge.net:/home/groups/t/ta/taskcoach/htdocs' % username)
    print 'Done uploading website to SourceForge.'
    
def registerWithPyPI(settings):
    print 'Registering with PyPI...'
    username = settings.get('pypi', 'username')
    password = settings.get('pypi', 'password')
    pypirc = file('.pypirc', 'w')
    pypirc.write('[server-login]\nusername = %s\npassword = %s\n'%\
                 (username, password))
    pypirc.close()
    from setup import setupOptions
    languagesThatPyPIDoesNotRecognize = ['Breton', 'Estonian', 'Galician', 
                                         'Lithuanian', 'Norwegian (Bokmal)',
                                         'Norwegian (Nynorsk)', 'Slovene']
    for language in languagesThatPyPIDoesNotRecognize:
        setupOptions['classifiers'].remove('Natural Language :: %s'%language)
    from distutils.core import setup
    del sys.argv[1:]
    os.environ['HOME'] = '.'
    sys.argv.append('register')
    setup(**setupOptions)
    os.remove('.pypirc')
    print 'Done registering with PyPI.'

def uploadWebsite(settings):
    uploadWebsiteToChello(settings)
    uploadWebsiteToSourceForge(settings)
    
def phase1(settings):
    uploadDistributionsToSourceForge(settings)
    generateMD5Digests(settings)
    generateWebsite(settings)
    
def phase2(settings):
    uploadWebsite(settings)
    registerWithPyPI(settings)

def mailAnnouncement(settings):
    server = settings.get('smtp', 'hostname')
    port = settings.get('smtp', 'port')
    username = settings.get('smtp', 'username')
    password = settings.get('smtp', 'password')
    sender_name = settings.get('smtp', 'sender_name')
    sender_email_address = settings.get('smtp', 'sender_email_address')
    recipients = ['frank@niessink.com']
    metadata = taskcoachlib.meta.data.metaDict
    metadata.update(dict(sender_name=sender_name,
                         sender_email_address=sender_email_address))
    msg = '''To: frank@niessink.com
From: %(sender_name)s <%(sender_email_address)s>
Reply-To: %(author_email)s
Subject: [ANN] Release %(version)s of %(name)s

Hi,

We're happy to announce release %(version)s of %(name)s. @Insert release
summary here@

Bugs fixed:

@Insert bugs here@

Feature(s) added:

@Insert features here@

What is %(name)s?

%(name)s is a simple task manager that allows for hierarchical tasks, i.e. tasks in tasks. %(name)s is open source (%(license_abbrev)s) and is developed using Python and wxPython. You can download %(name)s from:

%(url)s

In addition to the source distribution, packaged distributions are available for Windows XP/Vista, Mac OS X, and Linux (Debian and RPM format).

Note that %(name)s is %(release_status)s software. We do our best to prevent bugs, but it is always wise to back up your task file regularly, and especially when upgrading to a new release.

Regards, Jerome and Frank
'''%metadata
    session = smtplib.SMTP(server, port)
    session.set_debuglevel(1)
    session.helo()
    session.starttls()
    session.ehlo()
    session.login(username, password)
    smtpresult = session.sendmail(username, recipients, msg)

    if smtpresult:
        errstr = ""
        for recip in smtpresult.keys():
            errstr = """Could not delivery mail to: %s 
Server said: %s
%s
%s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
        raise smtplib.SMTPException, errstr


commands = dict(phase1=phase1, phase2=phase2, website=uploadWebsite, 
                websiteChello=uploadWebsiteToChello, 
                websiteSF=uploadWebsiteToSourceForge, 
                pypi=registerWithPyPI)#, announce=mailAnnouncement)
settings = Settings()
try:
    commands[sys.argv[1]](settings)
except (KeyError, IndexError):
    print 'Usage: release.py [%s]'%'|'.join(sorted(commands.keys()))
