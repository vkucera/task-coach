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
- Tag source code: cvs tag ReleaseX_Y_Z.
- Create branch if feature release: cvs tag -b ReleaseX_Y_Branch 
- Add release to Sourceforge bug tracker groups.
- Set bug reports and/or feature requests to Pending state.
'''

import ftplib, taskcoachlib.meta, os, glob, sys, md5

def uploadDistributionsToSourceForge():
    print 'Uploading distributions to SourceForge...'
    os.system('ncftpput upload.sourceforge.net incoming dist/*')
    print 'Done uploading distributions to SourceForge.'

def generateMD5Digests():
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


def generateWebsite():
    print 'Generating website...'
    os.chdir('website.in')
    os.system('python make.py')
    os.chdir('..')
    print 'Done generating website...'


class SimpleFTP(ftplib.FTP, object):
    def __init__(self, server, login, password_file):
        password = file(password_file).read()
        super(SimpleFTP, self).__init__(server, login, password)

    def delete(self, filenames):
        for filename in filenames:
            try:
                super(SimpleFTP, self).delete(filename)
                print 'Deleted %s'%filename
            except ftplib.error_perm:
                print "Couldn't delete %s"%filename

    def put(self, filenames):
        for filename in filenames:
            if os.path.isdir(filename):
                continue
            fd = file(filename, 'rb')
            self.storbinary('STOR %s'%filename, fd)
            print 'Stored %s'%filename

def uploadWebsiteToChello():
    print "Uploading website to Chello..."
    chello = SimpleFTP('members.chello.nl', 'f.niessink', '.chello_password')
    os.chdir('website.out')
    chello.put(glob.glob('*') + glob.glob('*/*'))
    chello.quit()
    os.chdir('..')
    print 'Done uploading website to Chello.'

def uploadWebsiteToSourceForge():
    print 'Uploading website to SourceForge...'
    os.system('scp -r website.out/* fniessink@shell.sourceforge.net:/home/groups/t/ta/taskcoach/htdocs')
    print 'Done uploading website to SourceForge.'
    
def registerWithPyPI():
    print 'Registering with PyPI...'
    from setup import setupOptions
    from distutils.core import setup
    import sys, os
    os.environ['HOME'] = '.'
    del sys.argv[1:]
    sys.argv.append('register')
    setup(**setupOptions)
    print 'Done registering with PyPI.'

def uploadWebsite():
    uploadWebsiteToChello()
    uploadWebsiteToSourceForge()
    
def phase1():
    uploadDistributionsToSourceForge()
    generateMD5Digests()
    generateWebsite()
    
def phase2():
    uploadWebsite()
    registerWithPyPI()


commands = dict(phase1=phase1, phase2=phase2, website=uploadWebsite)
try:
    commands[sys.argv[1]]()
except (KeyError, IndexError):
    print 'Usage: release.py [phase1|phase2|website]'
