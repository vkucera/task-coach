'''
Release steps:
- make clean all 
- make releasetests 
- Run this script to upload the distributions to sourceforge, generate MD5 
  digests and publish to Sourceforge Website, Chello (my ISP) and PyPI 
  (Python Package Index).
- Add file releases on sourceforge.net by hand
- Post project news on sourceforge.net by hand.
- Post release notification on freshmeat.net by hand.
- Tag source code: cvs tag ReleaseX_Y.
- Email taskcoach@yahoogroups.com and python-announce@python.org.
- Add release to Sourceforge bug tracker groups.
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
            fd = file(filename, 'rb')
            self.storbinary('STOR %s'%filename, fd)
            print 'Stored %s'%filename

def ftpWebsiteToChello():
    print "Uploading website to Chello..."
    chello = SimpleFTP('members.chello.nl', 'f.niessink', '.chello_password')
    os.chdir('website.out')
    chello.put(glob.glob('*'))
    chello.quit()
    os.chdir('..')
    print 'Done uploading website to Chello.'

def scpWebsiteToSourceForge():
    print 'Uploading website to SourceForge...'
    os.system('scp website.out/* fniessink@shell.sourceforge.net:/home/groups/t/ta/taskcoach/htdocs')
    print 'Done uploading website to SourceForge.'
    
def registerWithPyPI():
    print 'Registering with PyPI...'
    from setup import setupOptions
    from distutils.core import setup
    import sys, os
    os.environ['HOME'] = '.'
    sys.argv.append('register')
    setup(**setupOptions)
    print 'Done registering with PyPI.'

uploadDistributionsToSourceForge()
generateMD5Digests()
generateWebsite()
ftpWebsiteToChello()
scpWebsiteToSourceForge()
registerWithPyPI()
