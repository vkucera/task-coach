#!/usr/bin/env python

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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


HELP_TEXT = '''
Release steps:
  - Get latest translations from Launchpad:
    * Go to https://translations.launchpad.net/taskcoach/<major.minor>/+export
    * Wait for the confirmation email from Launchpad and copy the URL
    * Run 'cd i18n.in && python make.py <url>' to update the translations
    * Run 'make languagetests' to test the translations
    * When all tests pass, run 'svn commit -m "Updated translations"' 
  - Run 'make reallyclean' to remove old packages.
  - Run 'make alltests'.
  - Go to http://www.fraca7.net:8010/builders/Release to build releases.
  - For platforms not supported by the release builder, create and upload the 
    packages manually:
    * Mac OS X 10.4:        'make dmg; release.py upload'
    * Ubuntu 10.04:         'make deb; release.py upload'
    * Fedora 14:            'make fedora; release.py upload'
                            'make rpm; release.py upload'
    * OpenSuse:             'make opensuse; release.py upload'
    * Windows:              'make windists; release.py upload'
  - Mark the Windows and Mac OS X distributions as defaults for their platform:
    https://sourceforge.net/project/admin/explorer.php?group_id=130831#
    Navigate into the folder of the latest release and click on the Windows
    and Mac OS X distributions to set them as default download.
  - Run 'python release.py release' to download the distributions from
    Sourceforge, generate MD5 digests, generate the website, upload the 
    website to the Dreamhost and Hostland websites, announce the release on 
    Twitter, Identi.ca, Freecode and PyPI (Python Package Index), send the 
    announcement email, and to tag the release in Subversion.
  - Create branch if feature release.
  - Merge recent changes to the trunk.
  - Add release to Sourceforge bug tracker and support request groups.
  - Set bug reports on Sourceforge to Pending state.
  - Mark feature requests on Uservoice completed.
  - If new release branch, update the buildbot masters configuration.
'''

import ftplib
import smtplib
import httplib
import urllib
import os
import glob
import sys
import getpass
import hashlib
import base64
import ConfigParser
import simplejson
import codecs
import optparse
import taskcoachlib.meta
import oauth2 as oauth

# pylint: disable=W0621,W0613


def progress(func):
    ''' Decorator to print out a message when a release step starts and print
        a message when the release step is finished. '''
    def inner(*args, **kwargs):
        step = func.__name__.replace('_', ' ')
        print step[0].upper() + step[1:] + '...'
        func(*args, **kwargs)
        print 'Done %s.' % step
    return inner


class Settings(ConfigParser.SafeConfigParser, object):
    def __init__(self):
        super(Settings, self).__init__()
        self.set_defaults()
        self.filename = os.path.expanduser('~/.tcreleaserc')
        self.read(self.filename)

    def set_defaults(self):
        defaults = dict(sourceforge=['username', 'password'],
                        smtp=['hostname', 'port', 'username', 'password',
                              'sender_name', 'sender_email_address'],
                        dreamhost=['hostname', 'username', 'password', 
                                   'folder'],
                        hostland=['hostname', 'username', 'password', 'folder'],
                        pypi=['username', 'password'],
                        twitter=['consumer_key', 'consumer_secret',
                                 'oauth_token', 'oauth_token_secret'],
                        identica=['username', 'password'],
                        freecode=['auth_code'])
        for section in defaults:
            self.add_section(section)
            for option in defaults[section]:
                self.set(section, option, 'ask')

    def get(self, section, option):  # pylint: disable=W0221
        value = super(Settings, self).get(section, option)
        if value == 'ask':
            get_input = getpass.getpass if option == 'password' else raw_input
            value = get_input('%s %s: ' % (section, option)).strip()
            self.set(section, option, value)
            self.write(file(self.filename, 'w'))
        return value


class HelpFormatter(optparse.IndentedHelpFormatter):
    ''' Don't mess up the help text formatting. '''
    def format_epilog(self, epilog):
        return epilog
    

def sourceforge_location(settings):
    metadata = taskcoachlib.meta.data.metaDict
    project = metadata['filename_lower']
    project_first_two_letters = project[:2]
    project_first_letter = project[0]
    username = '%s,%s' % (settings.get('sourceforge', 'username'), project)
    folder = '/home/frs/project/%(p)s/%(pr)s/%(project)s/%(project)s/' \
             'Release-%(version)s/' % dict(project=project, 
                                           pr=project_first_two_letters, 
                                           p=project_first_letter, 
                                           version=metadata['version'])
    return '%s@frs.sourceforge.net:%s' % (username, folder)


def rsync(settings, options, rsync_command):
    location = sourceforge_location(settings)
    rsync_command = rsync_command % location
    if options.dry_run:
        print 'Skipping %s.' % rsync_command
    else:
        os.system(rsync_command)


@progress
def uploading_distributions_to_SourceForge(settings, options):
    rsync(settings, options, 'rsync -avP -e ssh dist/* %s')


@progress
def downloading_distributions_from_SourceForge(settings, options):
    rsync(settings, options, 'rsync -avP -e ssh %s dist/')


@progress
def generating_MD5_digests(settings, options):
    contents = '''md5digests = {\n'''
    for filename in glob.glob(os.path.join('dist', '*')):
        
        md5digest = hashlib.md5(file(filename, 'rb').read())  # pylint: disable=E1101
        filename = os.path.basename(filename)
        hexdigest = md5digest.hexdigest()
        contents += '''    "%s": "%s",\n''' % (filename, hexdigest)
        if options.verbose:
            print '%40s -> %s' % (filename, hexdigest)
    contents += '}\n'
    
    md5digests_file = file(os.path.join('website.in', 'md5digests.py'), 'w')
    md5digests_file.write(contents)
    md5digests_file.close()


@progress
def generating_website(settings, options):
    os.chdir('website.in')
    os.system('python make.py')
    os.chdir('..')


class SimpleFTP(ftplib.FTP, object):
    def __init__(self, hostname, username, password, folder='.'):
        super(SimpleFTP, self).__init__(hostname, username, password)
        self.ensure_folder(folder)
        self.remote_root = folder
            
    def ensure_folder(self, folder):
        try:
            self.cwd(folder)
        except ftplib.error_perm:
            self.mkd(folder)
            self.cwd(folder)    
            
    def put(self, folder, *filename_whitelist):
        for root, subfolders, filenames in os.walk(folder):
            if root != folder:
                print 'Change into %s' % root
                for part in root.split(os.sep):
                    self.cwd(part)
            for subfolder in subfolders:
                print 'Create %s' % os.path.join(root, subfolder)
                try:
                    self.mkd(subfolder)
                except ftplib.error_perm, info:
                    print info
            for filename in filenames:
                if filename_whitelist and filename not in filename_whitelist:
                    print 'Skipping %s' % os.path.join(root, filename)
                    continue
                print 'Store %s' % os.path.join(root, filename)
                try:
                    self.storbinary('STOR %s' % filename, 
                                    file(os.path.join(root, filename), 'rb'))
                except ftplib.error_perm, info:
                    if str(info).endswith('Overwrite permission denied'):
                        self.delete(filename)
                        self.storbinary('STOR %s' % filename, 
                                        file(os.path.join(root, filename), 
                                             'rb'))
                    else:
                        raise
            self.cwd(self.remote_root)

    def get(self, filename):
        print 'Retrieve %s' % filename
        self.retrbinary('RETR %s' % filename, open(filename, 'wb').write)


def uploading_website_to_website_host(settings, options, website_host, 
                                      *filename_whitelist):
    settings_section = website_host.lower()
    hostname = settings.get(settings_section, 'hostname')
    username = settings.get(settings_section, 'username')
    password = settings.get(settings_section, 'password')
    folder = settings.get(settings_section, 'folder')
    
    if hostname and username and password and folder:
        ftp = SimpleFTP(hostname, username, password, folder)
        os.chdir('website.out')
        if options.dry_run:
            print 'Skipping ftp.put(website.out).'
        else:
            ftp.put('.', *filename_whitelist)
        ftp.quit()
        os.chdir('..')
    else:
        print 'Warning: cannot upload website to %s; missing credentials' % \
            website_host


@progress
def uploading_website_to_Dreamhost(settings, options, *args):
    uploading_website_to_website_host(settings, options, 'Dreamhost', *args)
 

@progress
def uploading_website_to_Hostland(settings, options, *args):
    uploading_website_to_website_host(settings, options, 'Hostland', *args)


@progress
def registering_with_PyPI(settings, options):
    username = settings.get('pypi', 'username')
    password = settings.get('pypi', 'password')
    pypirc = file('.pypirc', 'w')
    pypirc.write('[server-login]\nusername = %s\npassword = %s\n' % \
                 (username, password))
    pypirc.close()
    # pylint: disable=W0404
    from setup import setupOptions
    languages_pypi_does_not_know = ['Basque', 'Belarusian', 'Breton', 
        'Estonian', 'Galician', 'Lithuanian', 'Norwegian (Bokmal)', 
        'Norwegian (Nynorsk)', 'Occitan', 'Papiamento', 'Slovene', 
        'German (Low)', 'Mongolian']
    for language in languages_pypi_does_not_know:
        setupOptions['classifiers'].remove('Natural Language :: %s' % language)
    from distutils.core import setup
    del sys.argv[1:]
    os.environ['HOME'] = '.'
    sys.argv.append('register')
    if options.dry_run:
        print 'Skipping PyPI registration.'
    else:
        setup(**setupOptions)  # pylint: disable=W0142
    os.remove('.pypirc')


def postRequest(connection, api_call, body, contentType, ok=200, **headers):
    headers['Content-Type'] = contentType
    connection.request('POST', api_call, body, headers)
    response = connection.getresponse()
    if response.status != ok:
        print 'Request failed: %d %s' % (response.status, response.reason)


def httpPostRequest(host, api_call, body, contentType, ok=200, **headers):
    connection = httplib.HTTPConnection(host)
    postRequest(connection, api_call, body, contentType, ok, **headers)


def httpsPostRequest(host, api_call, body, contentType, ok=200, **headers):
    connection = httplib.HTTPSConnection(host)
    postRequest(connection, api_call, body, contentType, ok, **headers)


@progress
def announcing_on_Freecode(settings, options):
    auth_code = settings.get('freecode', 'auth_code')
    metadata = taskcoachlib.meta.data.metaDict
    version = '%(version)s' % metadata
    changelog = latest_release(metadata, summary_only=True)
    tag = 'Feature enhancements' if version.endswith('.0') else 'Bug fixes'
    release = dict(version=version, changelog=changelog, tag_list=tag)
    body = codecs.encode(simplejson.dumps(dict(auth_code=auth_code, 
                                               release=release)))
    path = '/projects/taskcoach/releases.json'
    host = 'freecode.com'
    if options.dry_run:
        print 'Skipping announcing "%s" on %s.' % (release, host)
    else:
        httpsPostRequest(host, path, body, 'application/json', ok=201)


def status_message():
    ''' Return a brief status message for e.g. Twitter. '''
    metadata = taskcoachlib.meta.data.metaDict
    return "Release %(version)s of %(name)s is available from %(url)s. " \
           "See what's new at %(url)schanges.html." % metadata


def announcing_via_Basic_Auth_Api(settings, options, section, host, 
                                  api_prefix=''):
    credentials = ':'.join(settings.get(section, credential) \
                           for credential in ('username', 'password'))
    basic_auth = base64.encodestring(credentials)[:-1]
    status = status_message()
    api_call = api_prefix + '/statuses/update.json'
    body = '='.join((urllib.quote(body_part.encode('utf-8')) \
                     for body_part in ('status', status)))
    if options.dry_run:
        print 'Skipping announcing "%s" on %s.' % (status, host)
    else:
        httpPostRequest(host, api_call, body, 
                        'application/x-www-form-urlencoded; charset=utf-8',
                        Authorization='Basic %s' % basic_auth)


def announcing_via_OAuth_Api(settings, options, section, host):
    consumer_key = settings.get(section, 'consumer_key')
    consumer_secret = settings.get(section, 'consumer_secret')
    consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    oauth_token = settings.get(section, 'oauth_token')
    oauth_token_secret = settings.get(section, 'oauth_token_secret')
    token = oauth.Token(key=oauth_token, secret=oauth_token_secret)
    client = oauth.Client(consumer, token)
    status = status_message()
    if options.dry_run:
        print 'Skipping announcing "%s" on %s.' % (status, host)
    else: 
        response, dummy_content = client.request( \
            'http://api.%s/1/statuses/update.json' % host, method='POST', 
            body='status=%s' % status, headers=None)
        if response.status != 200:
            print 'Request failed: %d %s' % (response.status, response.reason)


@progress
def announcing_on_Twitter(settings, options):
    announcing_via_OAuth_Api(settings, options, 'twitter', 'twitter.com')


@progress
def announcing_on_Identica(settings, options):
    announcing_via_Basic_Auth_Api(settings, options, 'identica', 'identi.ca', 
                                  '/api')


def uploading_website(settings, options, *args):
    ''' Upload the website contents to the website(s). If args is present
        only the files specified in args are uploaded. '''
    uploading_website_to_Dreamhost(settings, options, *args)
    uploading_website_to_Hostland(settings, options, *args)
    

def announcing(settings, options):
    registering_with_PyPI(settings, options)
    announcing_on_Twitter(settings, options)
    announcing_on_Identica(settings, options)
    announcing_on_Freecode(settings, options)
    mailing_announcement(settings, options)


def releasing(settings, options):
    downloading_distributions_from_SourceForge(settings, options)
    generating_MD5_digests(settings, options)
    generating_website(settings, options)
    uploading_website(settings, options)
    announcing(settings, options)
    tagging_release_in_subversion(settings, options)


def latest_release(metadata, summary_only=False):
    sys.path.insert(0, 'changes.in')
    # pylint: disable=F0401
    import changes 
    import converter  
    del sys.path[0]
    greeting = 'release %(version)s of %(name)s.' % metadata
    if summary_only:
        greeting = greeting[0].upper() + greeting[1:] 
    else:
        greeting = "We're happy to announce " + greeting
    text_converter = converter.ReleaseToTextConverter()
    convert = text_converter.summary if summary_only else text_converter.convert
    return convert(changes.releases[0], greeting)


@progress
def mailing_announcement(settings, options):
    metadata = taskcoachlib.meta.data.metaDict
    for sender_info in 'sender_name', 'sender_email_address':
        metadata[sender_info] = settings.get('smtp', sender_info)
    metadata['release'] = latest_release(metadata)
    msg = '''To: %(announcement_addresses)s
BCC: %(bcc_announcement_addresses)s
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
for Windows, Mac OS X, Linux, and BSD.

Note that although we consider %(name)s to be %(release_status)s software,
and we do our best to prevent bugs, it is always wise to back up your task 
file regularly, and especially when upgrading to a new release.

Regards, 

%(author)s
Task Coach development team

''' % metadata

    recipients = metadata['announcement_addresses']
    server = settings.get('smtp', 'hostname')
    port = settings.get('smtp', 'port')
    username = settings.get('smtp', 'username')
    password = settings.get('smtp', 'password')

    session = smtplib.SMTP(server, port)
    if options.verbose:
        session.set_debuglevel(1)
    session.helo()
    session.ehlo()
    session.starttls()
    session.esmtp_features["auth"] = "LOGIN"  # Needed for Gmail SMTP.
    session.login(username, password)
    if options.dry_run:
        print 'Skipping sending mail.'
        smtpresult = None
    else:
        smtpresult = session.sendmail(username, recipients, msg)

    if smtpresult:
        errstr = ""
        for recip in smtpresult.keys():
            errstr = """Could not deliver mail to: %s 
Server said: %s
%s
%s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
        raise smtplib.SMTPException, errstr


@progress
def tagging_release_in_subversion(settings, options):
    metadata = taskcoachlib.meta.data.metaDict
    version = metadata['version']
    username = settings.get('sourceforge', 'username') 
    release_tag = 'Release' + version.replace('.', '_')
    target_url = 'svn+ssh://%s@svn.code.sf.net/p/taskcoach/code/tags/' % \
                 username + release_tag
    commit_message = 'Tag for release %s.' % version
    svn_copy = 'svn copy -m "%s" . %s' % (commit_message, target_url)
    if options.dry_run:
        print 'Skipping %s.' % svn_copy
    else:
        os.system(svn_copy)
     
   
COMMANDS = dict(release=releasing,
                upload=uploading_distributions_to_SourceForge, 
                download=downloading_distributions_from_SourceForge, 
                md5=generating_MD5_digests,
                website=uploading_website,
                websiteDH=uploading_website_to_Dreamhost,
                websiteHL=uploading_website_to_Hostland,
                twitter=announcing_on_Twitter,
                identica=announcing_on_Identica,
                freecode=announcing_on_Freecode,
                pypi=registering_with_PyPI, 
                mail=mailing_announcement,
                announce=announcing,
                tag=tagging_release_in_subversion)

USAGE = 'Usage: %%prog [options] [%s]' % '|'.join(sorted(COMMANDS.keys()))

SETTINGS = Settings()

parser = optparse.OptionParser(usage=USAGE, epilog=HELP_TEXT, 
                               formatter=HelpFormatter())
parser.add_option('-n', '--dry-run', action='store_true', dest='dry_run', 
                  help="don't make permanent changes")
parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                  help='provide more detailed progress information')
options, args = parser.parse_args()

try:
    if len(args) > 1:
        COMMANDS[args[0]](SETTINGS, options, *args[1:])  # pylint: disable=W0142
    else:
        COMMANDS[args[0]](SETTINGS, options)
except (KeyError, IndexError):
    parser.print_help()
