#!/usr/bin/env python

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Frank Niessink <frank@niessink.com>

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

helpText = '''
Release steps:

- Get latest translations from Launchpad.

- Run 'make clean all'.

- Run 'make alltests'.

- For each platform, create and upload the packages:
  MaC OS X:    'make clean dmg; python release.py upload'
  Ubuntu 8.04: 'make clean sdist_linux deb; python release.py upload'
  Ubuntu 9.10: 'make clean sdist_linux deb; python release.py upload'
  Fedora 11:   'make clean fedora; python release.py upload'
  OpenSuse:    'make clean opensuse; python release.py upload'
  Windows:     'make clean windists; python release.py upload'

- Mark the Windows and Mac OS X distributions as defaults for their platform:
  https://sourceforge.net/project/admin/explorer.php?group_id=130831#
  Navigate into the folder of the latest release and click on the Windows
  and Mac OS X distributions to set them as default download.

- Run 'python release.py release' to download the distributions from
  Sourceforge, generate MD5 digests, generate the website, upload the 
  website to the Hypernation.net website and to Chello (Frank's ISP), 
  announce the release on Twitter, Identi.ca, Freshmeat and PyPI (Python 
  Package Index) and to send the announcement email.

- Tag source code with tag ReleaseX_Y_Z.

- Create branch if feature release.

- Merge recent changes to the trunk.

- Add release to Sourceforge bug tracker and support request groups.

- Set bug reports on Sourceforge to Pending state.

- Mark feature requests on Uservoice completed.

- If new release branch, update the buildbot masters configuration.
'''

import ftplib, smtplib, httplib, urllib, os, glob, sys, getpass, hashlib, \
    base64, ConfigParser, simplejson, codecs, taskcoachlib.meta


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
                        twitter=['username', 'password'],
                        identica=['username', 'password'],
                        freshmeat=['auth_code'])
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
    contents = '''md5digests = {\n'''
    for filename in glob.glob(os.path.join('dist', '*')):
        
        md5digest = hashlib.md5(file(filename, 'rb').read())
        filename = os.path.basename(filename)
        hexdigest = md5digest.hexdigest()
        contents += '''    "%s": "%s",\n'''%(filename, hexdigest)
        print 'MD5 digest for %s is %s'%(filename, hexdigest)
    contents += '}\n'
    
    print 'Writing MD5 digests...'
    md5digestsFile = file(os.path.join('website.in', 'md5digests.py'), 'w')
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
        self.remote_root = folder
            
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
                for part in root.split(os.sep):
                    self.cwd(part)
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
            self.cwd(self.remote_root)

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
        'Slovene', 'German (Low)', 'Mongolian']
    for language in languagesThatPyPIDoesNotRecognize:
        setupOptions['classifiers'].remove('Natural Language :: %s'%language)
    from distutils.core import setup
    del sys.argv[1:]
    os.environ['HOME'] = '.'
    sys.argv.append('register')
    setup(**setupOptions)
    os.remove('.pypirc')
    print 'Done registering with PyPI.'


def httpPostRequest(host, api_call, body, contentType, ok=200, **headers):
    headers['Content-Type'] = contentType
    connection = httplib.HTTPConnection('%s:80'%host)
    connection.request('POST', api_call, body, headers)
    response = connection.getresponse()
    if response.status != ok:
        print 'Request failed: %d %s'%(response.status, response.reason)


def announceOnFreshmeat(settings):
    print 'Announcing on Freshmeat...'
    auth_code = settings.get('freshmeat', 'auth_code')
    metadata = taskcoachlib.meta.data.metaDict
    version = '%(version)s'%metadata
    changelog = latest_release(metadata, summaryOnly=True)
    tag = 'Feature enhancements' if version.endswith('.0') else 'Bug fixes'
    release = dict(version=version, changelog=changelog, tag_list=tag)
    body = codecs.encode(simplejson.dumps(dict(auth_code=auth_code, 
                                               release=release)))
    path = '/projects/taskcoach/releases.json'
    httpPostRequest('freshmeat.net', path, body, 'application/json', ok=201)
    print 'Done announcing on Freshmeat.'


def announceViaTwitterApi(settings, section, host, api_prefix=''):
    print 'Announcing on %s...'%host
    credentials = ':'.join(settings.get(section, credential) \
                           for credential in ('username', 'password'))
    basic_auth = base64.encodestring(credentials)[:-1]
    metadata = taskcoachlib.meta.data.metaDict
    status = 'Release %(version)s of %(name)s is available from %(url)s'%metadata
    connection = httplib.HTTPConnection('%s:80'%host)
    api_call = api_prefix + '/statuses/update.json'
    body = '='.join((urllib.quote(body_part.encode('utf-8')) \
                     for body_part in ('status', status)))
    httpPostRequest(host, api_call, body, 
                    'application/x-www-form-urlencoded; charset=utf-8',
                    Authorization='Basic %s'%basic_auth)
    print 'Done announcing on %s.'%host


def announceOnTwitter(settings):
    announceViaTwitterApi(settings, 'twitter', 'twitter.com')
    

def announceOnIdentica(settings):
    announceViaTwitterApi(settings, 'identica', 'identi.ca', '/api')


def uploadWebsite(settings):
    uploadWebsiteToChello(settings)
    uploadWebsiteToHypernation(settings)
    

def announce(settings):
    registerWithPyPI(settings)
    announceOnTwitter(settings)
    announceOnIdentica(settings)
    announceOnFreshmeat(settings)
    mailAnnouncement(settings)


def release(settings):
    downloadDistributionsFromSourceForge(settings)
    generateMD5Digests(settings)
    generateWebsite(settings)
    uploadWebsite(settings)
    announce(settings)


def latest_release(metadata, summaryOnly=False):
    sys.path.insert(0, 'changes.in')
    import changes, converter
    del sys.path[0]
    greeting = 'release %(version)s of %(name)s.'%metadata
    if summaryOnly:
        greeting = greeting.capitalize() 
    else:
        greeting = "We're happy to announce " + greeting
    textConverter = converter.ReleaseToTextConverter()
    convert = textConverter.summary if summaryOnly else textConverter.convert
    return convert(changes.releases[0], greeting)


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


def help(settings):
    print helpText


commands = dict(release=release,
                upload=uploadDistributionsToSourceForge, 
                download=downloadDistributionsFromSourceForge, 
                md5=generateMD5Digests,
                website=uploadWebsite, 
                websiteChello=uploadWebsiteToChello, 
                websiteHN=uploadWebsiteToHypernation,
                twitter=announceOnTwitter,
                identica=announceOnIdentica,
                freshmeat=announceOnFreshmeat,
                pypi=registerWithPyPI, 
                mail=mailAnnouncement,
                announce=announce,
                help=help)
settings = Settings()
try:
    commands[sys.argv[1]](settings)
except (KeyError, IndexError):
    print 'Usage: release.py [%s]'%'|'.join(sorted(commands.keys()))
