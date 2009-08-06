#!/usr/bin/env python

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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

- Get latest translations from Launchpad.

- Run 'make clean all'.

- Run 'make alltests'.

- For each platform, create and upload the packages:
  MaC OS X:  'make clean dmg; python release.py upload'
  Ubuntu:    'make clean deb; python release.py upload'
  Fedora 8:  'make clean fedora; python release.py upload', and
             'make clean rpm; python release.py upload'
  Fedora 11: 'make clean fedora; python release.py upload'
  Windows:   'make clean windist; python release.py upload'

- Mark the Windows and Mac OS X distributions as defaults for their platform:
  https://sourceforge.net/project/admin/explorer.php?group_id=130831#
  Navigate into the folder of the latest release and click on the Windows
  and Mac OS X distributions to set them as default download.

- Run 'python release.py release' to download the distributions from
  Sourceforge, generate MD5 digests, generate the website, upload the 
  website to the Hypernation.net website and to Chello (Frank's ISP), 
  announce the release on Twitter and PyPI (Python Package Index) and to 
  send the announcement email.

- Post release notification on Freshmeat and Identi.ca by hand.

- Tag source code with tag ReleaseX_Y_Z.

- Create branch if feature release.

- Merge recent changes to the trunk.

- Add release to Sourceforge bug tracker groups.

- Set bug reports and/or feature requests to Pending state.

- If new release branch, update the buildbot masters configuration.
'''

import ftplib, smtplib, os, glob, sys, getpass, hashlib, ConfigParser, \
    twitter, taskcoachlib.meta

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
                        chello=['hostname', 'username', 'password', 'folder'],
                        hypernation=['hostname', 'username', 'password', 'folder'],
                        pypi=['username', 'password'],
                        twitter=['username', 'password'])
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


def sourceForgeLocation(settings):
    metadata = taskcoachlib.meta.data.metaDict
    project = metadata['filename_lower']
    pr = project[:2]
    p = project[0]
    username = '%s,%s'%(settings.get('sourceforge', 'username'), project)
    folder = '/home/frs/project/%(p)s/%(pr)s/%(project)s/%(project)s/Release-%(version)s/'%\
             dict(project=project, pr=pr, p=p, version=metadata['version'])
    return '%s@frs.sourceforge.net:%s'%(username, folder)


def uploadDistributionsToSourceForge(settings):
    print 'Uploading distributions to SourceForge...'
    location = sourceForgeLocation(settings)
    os.system('rsync -avP -e ssh dist/* %s'%location)
    print 'Done uploading distributions to SourceForge.'


def downloadDistributionsFromSourceForge(settings):
    print 'Downloading distributions from SourceForge...'
    location = sourceForgeLocation(settings)
    os.system('rsync -avP -e ssh %s dist/'%location)
    print 'Done downloading distributions from SourceForge.'



def generateMD5Digests(settings):
    print 'Generating MD5 digests...'
    contents = '''<TABLE>
    <TR>
        <TH ALIGN='LEFT'>Filename</TH>
        <TH ALIGN='LEFT'>MD5 digest</TH>
    </TR>
'''
    for filename in glob.glob(os.path.join('dist', '*')):
        
        md5digest = hashlib.md5(file(filename, 'rb').read())
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
    def __init__(self, hostname, username, password, folder='.'):
        super(SimpleFTP, self).__init__(hostname, username, password)
        self.ensure_folder(folder)
            
    def ensure_folder(self, folder):
        try:
            self.cwd(folder)
        except ftplib.error_perm, info:
            self.mkd(folder)
            self.cwd(folder)    
            
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

    def get(self, filename):
        print 'Retrieve %s'%filename
        self.retrbinary('RETR %s'%filename, open(filename, 'wb').write)



def uploadWebsiteToWebsiteHost(settings, websiteName):
    settingsSection = websiteName.lower()
    hostname = settings.get(settingsSection, 'hostname')
    username = settings.get(settingsSection, 'username')
    password = settings.get(settingsSection, 'password')
    folder = settings.get(settingsSection, 'folder')
    
    if hostname and username and password and folder:
        print 'Uploading website to %s...'%websiteName
        ftp = SimpleFTP(hostname, username, password, folder)
        os.chdir('website.out')
        ftp.put('.')
        ftp.put('.htaccess')
        ftp.quit()
        os.chdir('..')
        print 'Done uploading website to %s.'%websiteName
    else:
        print 'Warning: cannot upload website to %s; missing credentials'%websiteName


def uploadWebsiteToChello(settings):
    uploadWebsiteToWebsiteHost(settings, 'Chello')


def uploadWebsiteToHypernation(settings):
    uploadWebsiteToWebsiteHost(settings, 'Hypernation')

 
def registerWithPyPI(settings):
    print 'Registering with PyPI...'
    username = settings.get('pypi', 'username')
    password = settings.get('pypi', 'password')
    pypirc = file('.pypirc', 'w')
    pypirc.write('[server-login]\nusername = %s\npassword = %s\n'%\
                 (username, password))
    pypirc.close()
    from setup import setupOptions
    languagesThatPyPIDoesNotRecognize = ['Basque', 'Breton', 'Estonian', 
        'Galician', 'Lithuanian', 'Norwegian (Bokmal)', 'Norwegian (Nynorsk)', 
        'Slovene', 'German (Low)']
    for language in languagesThatPyPIDoesNotRecognize:
        setupOptions['classifiers'].remove('Natural Language :: %s'%language)
    from distutils.core import setup
    del sys.argv[1:]
    os.environ['HOME'] = '.'
    sys.argv.append('register')
    setup(**setupOptions)
    os.remove('.pypirc')
    print 'Done registering with PyPI.'


def announceOnTwitter(settings):
    print 'Announcing on twitter...'
    username = settings.get('twitter', 'username')
    password = settings.get('twitter', 'password')
    metadata = taskcoachlib.meta.data.metaDict
    api = twitter.Api(username=username, password=password)
    api.PostUpdate('Release %(version)s of %(name)s is available from %(url)s'%metadata)
    print 'Done announcing on twitter.'


def uploadWebsite(settings):
    uploadWebsiteToChello(settings)
    uploadWebsiteToHypernation(settings)
    

def announce(settings):
    registerWithPyPI(settings)
    announceOnTwitter(settings)
    mailAnnouncement(settings)


def release(settings):
    downloadDistributionsFromSourceForge(settings)
    generateMD5Digests(settings)
    generateWebsite(settings)
    uploadWebsite(settings)
    announce(settings)


def latest_release(metadata):
    sys.path.insert(0, 'changes.in')
    import changes, converter
    del sys.path[0]
    return converter.ReleaseToTextConverter().convert(changes.releases[0],
        greeting="We're happy to announce release %(version)s "
                  "of %(name)s."%metadata)


def mailAnnouncement(settings):
    metadata = taskcoachlib.meta.data.metaDict
    for sender_info in 'sender_name', 'sender_email_address':
        metadata[sender_info] = settings.get('smtp', sender_info)
    metadata['release'] = latest_release(metadata)
    msg = '''To: %(announcement_addresses)s
From: %(sender_name)s <%(sender_email_address)s>
Reply-To: %(author_email)s
Subject: [ANN] Release %(version)s of %(name)s

Hi,

%(release)s

What is %(name)s?

%(name)s is a simple task manager that allows for hierarchical tasks, 
i.e. tasks in tasks. %(name)s is open source (%(license_abbrev)s) and is developed 
using Python and wxPython. You can download %(name)s from:

%(url)s

In addition to the source distribution, packaged distributions are available 
for Windows XP/Vista, Mac OS X, and Linux (Debian and RPM format).

Note that %(name)s is %(release_status)s software. We do our best to prevent bugs, 
but it is always wise to back up your task file regularly, and especially 
when upgrading to a new release.

Regards, 

%(author)s
Task Coach development team

'''%metadata

    recipients = metadata['announcement_addresses']
    server = settings.get('smtp', 'hostname')
    port = settings.get('smtp', 'port')
    username = settings.get('smtp', 'username')
    password = settings.get('smtp', 'password')

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
            errstr = """Could not deliver mail to: %s 
Server said: %s
%s
%s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
        raise smtplib.SMTPException, errstr


commands = dict(release=release,
                upload=uploadDistributionsToSourceForge, 
                download=downloadDistributionsFromSourceForge, 
                md5=generateMD5Digests,
                website=uploadWebsite, 
                websiteChello=uploadWebsiteToChello, 
                websiteHN=uploadWebsiteToHypernation,
                twitter=announceOnTwitter, 
                pypi=registerWithPyPI, announce=mailAnnouncement)
settings = Settings()
try:
    commands[sys.argv[1]](settings)
except (KeyError, IndexError):
    print 'Usage: release.py [%s]'%'|'.join(sorted(commands.keys()))
