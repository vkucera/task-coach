'''
Release steps:
1. Run this script to release to Sourceforge Website, Chello (my ISP) and PyPI.
1a. Remove old TaskCoach releases from SF TC Website by hand (sftp)
2. Use releaseforge to release to Sourceforge.
2a. Upload distributions
2b. Post project news.
3. Post release notification on freshmeat.net by hand.
4. Tag source code: cvs tag ReleaseX_Y.
5. Email taskcoach@yahoogroups.com and python-announce@python.org.
6. Add release to Sourceforge bug tracker groups.
'''

import ftplib, taskcoachlib.meta, os, glob, sys

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
            fd = file(filename, 'rb')
            self.storbinary('STOR %s'%filename, fd)
            print 'Stored %s'%filename

def ftpToChello():
    previous_version = taskcoachlib.meta.previous_version
    chello = SimpleFTP('members.chello.nl', 'f.niessink', '.chello_password')
    os.chdir('dist')
    chello.delete([distro%previous_version for distro in
        ('TaskCoach-%s.tar.gz', 'TaskCoach-%s.zip', 'TaskCoach-%s-win32.exe')])
    chello.put(glob.glob('*'))
    chello.quit()

def scpToSourceForge():
    os.system('scp dist/* fniessink@shell.sourceforge.net:/home/groups/t/ta/taskcoach/htdocs')

def registerWithPyPI():
    from setup import setupOptions
    from distutils.core import setup
    import sys, os
    os.environ['HOME'] = '.'
    sys.argv.append('register')
    setup(**setupOptions)

ftpToChello()
#scpToSourceForge()
registerWithPyPI()
