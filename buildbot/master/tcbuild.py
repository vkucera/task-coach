#!/usr/bin/python

from buildbot.steps.shell import Compile, WithProperties
from buildbot.steps.transfer import FileUpload, DirectoryUpload
from buildbot import interfaces
from buildbot.process.buildstep import SUCCESS, FAILURE

from twisted.python import log

from zope.interface import implements

import os

class TaskCoachEmailLookup(object):
    implements(interfaces.IEmailLookup)

    def getAddress(self, name):
        try:
            return { 'fraca7': 'fraca7@free.fr',
                     'fniessink': 'frank@niessink.com' }[name]
        except KeyError:
            return None

class Cleanup(Compile):
    name = 'Cleanup'
    description = ['Deleting', 'unversioned', 'files']
    descriptionDone = ['Unversioned', 'files', 'deleted']

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'nuke']
        Compile.__init__(self, **kwargs)

class UnitTests(Compile):
    name = 'unit tests'
    description = ['Running', 'unit', 'tests']
    descriptionDone = ['Unit', 'tests']

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'unittests']
        # On several distros, some tests fail randomly. Just make sure
        # we still build the package and so on.
        kwargs['haltOnFailure'] = False
        Compile.__init__(self, **kwargs)

class IntegrationTests(Compile):
    name = 'integration tests'
    description = ['Running', 'integration', 'tests']
    descriptionDone = ['Integration', 'tests']

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'integrationtests']
        Compile.__init__(self, **kwargs)

class LanguageTests(Compile):
    name = 'language tests'
    description = ['Running', 'language', 'tests']
    descriptionDone = ['Language', 'tests']

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'languagetests']
        Compile.__init__(self, **kwargs)

class DistributionTests(Compile):
    name = 'distribution tests'
    description = ['Running', 'distribution', 'tests']
    descriptionDone = ['Distribution', 'tests']

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'disttests']
        Compile.__init__(self, **kwargs)

class Coverage(Compile):
    name = 'coverage'
    description = ['Running', 'coverage']
    descriptionDone = ['Coverage']

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'coverage']
        Compile.__init__(self, **kwargs)

    def createSummary(self, log):
        Compile.createSummary(self, log)

        self.addURL('coverage',
                    'http://www.fraca7.net/TaskCoach-coverage/%s/index.html' % (self.getProperty('buildername')))

class UploadCoverage(DirectoryUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = 'tests/coverage.out'
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-coverage/%s',
                                              'buildername')
        kwargs['mode'] = 0755
        kwargs['compress'] = None
        DirectoryUpload.__init__(self, **kwargs)

class Epydoc(Compile):
    name = 'epydoc'
    description = ['Generating', 'documentation']
    descriptionDone = ['Documentation']

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'epydoc']
        Compile.__init__(self, **kwargs)


#==============================================================================
# Platform-specific

class DistCompile(Compile):
    def __init__(self, **kwargs):
        kwargs['command'] = ['make', self.name,
                             WithProperties('TCVERSION=r%s', 'got_revision')]
        Compile.__init__(self, **kwargs)

class UploadBase(FileUpload):
    def filename(self):
        raise NotImplementedError

    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/%s' % self.filename(), 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-packages/%s' % self.filename(),
                                              'got_revision')
        kwargs['mode'] = 0644
        FileUpload.__init__(self, **kwargs)

class BuildDMG(DistCompile):
    name = 'dmg'
    description = ['Generating', 'MacOS', 'binary']
    descriptionDone = ['MacOS', 'binary']

    def createSummary(self, log):
        DistCompile.createSummary(self, log)
        self.addURL('download',
                    'http://www.fraca7.net/TaskCoach-packages/TaskCoach-r%s.dmg' % self.getProperty('got_revision'))

        cname = '/var/www/htdocs/TaskCoach-packages/TaskCoach-latest.dmg'
        if os.path.exists(cname):
            os.remove(cname)
        os.symlink('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s.dmg' % self.getProperty('got_revision'),
                   cname)

class UploadDMG(UploadBase):
    def filename(self):
        return 'TaskCoach-r%s.dmg'

class BuildEXE(DistCompile):
    name = 'windist'
    description = ['Generating', 'Windows', 'binary']
    descriptionDone = ['Windows', 'binary']

    def createSummary(self, log):
        # Not calling superclass here, because py2exe is pretty anal
        # about what should be a version number: at most 4
        # dot-separated numbers, so 'rXXXX' doesn't pass. This
        # procuces a meaningless warning.

        # In the near future, I'll arrange to build up a version
        # number in the form <actual version>.<current revision>.

        #DistCompile.createSummary(self, log)

        self.addURL('download',
                    'http://www.fraca7.net/TaskCoach-packages/TaskCoach-r%s-win32.exe' % self.getProperty('got_revision'))

        cname = '/var/www/htdocs/TaskCoach-packages/TaskCoach-latest-win32.exe'
        if os.path.exists(cname):
            os.remove(cname)
        os.symlink('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s-win32.exe' % self.getProperty('got_revision'),
                   cname)

class UploadEXE(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/TaskCoach-r%s-win32.exe', 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s-win32.exe', 'got_revision')
        kwargs['mode'] = 0644
        FileUpload.__init__(self, **kwargs)

class BuildSource(DistCompile):
    name = 'sdist'
    description = ['Generating', 'source', 'distribution']
    descriptionDone = ['Source', 'distribution']

    def createSummary(self, log):
        DistCompile.createSummary(self, log)
        self.addURL('download .tar.gz',
                    'http://www.fraca7.net/TaskCoach-packages/TaskCoach-r%s.tar.gz' % self.getProperty('got_revision'))
        self.addURL('download .zip',
                    'http://www.fraca7.net/TaskCoach-packages/TaskCoach-r%s.zip' % self.getProperty('got_revision'))

        cname = '/var/www/htdocs/TaskCoach-packages/TaskCoach-latest.tar.gz'
        if os.path.exists(cname):
            os.remove(cname)
        os.symlink('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s.tar.gz' % self.getProperty('got_revision'),
                   cname)

        cname = '/var/www/htdocs/TaskCoach-packages/TaskCoach-latest.zip'
        if os.path.exists(cname):
            os.remove(cname)
        os.symlink('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s.zip' % self.getProperty('got_revision'),
                   cname)

class UploadSourceTar(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/TaskCoach-r%s.tar.gz', 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s.tar.gz', 'got_revision')
        kwargs['mode'] = 0644
        FileUpload.__init__(self, **kwargs)

class UploadSourceZip(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/TaskCoach-r%s.zip', 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s.zip', 'got_revision')
        kwargs['mode'] = 0644
        FileUpload.__init__(self, **kwargs)

class BuildDEB(DistCompile):
    name = 'deb'
    description = ['Generating', 'Debian', 'package']
    descriptionDone = ['Debian', 'package']

    def createSummary(self, log):
        # Not calling parent because there are a bunch of warnings we
        # don't really care about.
        # DistCompile.createSummary(self, log)
        self.addURL('download',
                    'http://www.fraca7.net/TaskCoach-packages/taskcoach_r%s-1_all.deb' % self.getProperty('got_revision'))

        cname = '/var/www/htdocs/TaskCoach-packages/taskcoach_latest-1_all.deb'
        if os.path.exists(cname):
            os.remove(cname)
        os.symlink('/var/www/htdocs/TaskCoach-packages/taskcoach_r%s-1_all.deb' % self.getProperty('got_revision'),
                   cname)

class UploadDEB(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/taskcoach_r%s-1_all.deb', 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-packages/taskcoach_r%s-1_all.deb', 'got_revision')
        kwargs['mode'] = 0644
        FileUpload.__init__(self, **kwargs)

class BuildRPM(DistCompile):
    name = 'rpm'
    description = ['Generating', 'RPM', 'package']
    descriptiondone = ['RPM', 'package']

    def createSummary(self, log):
        # Not calling parent because there are a bunch of warnings we
        # don't really care about.
        # DistCompile.createSummary(self, log)
        self.addURL('download',
                    'http://www.fraca7.net/TaskCoach-packages/TaskCoach-r%s-1.noarch.rpm' % self.getProperty('got_revision'))

        self.addURL('download',
                    'http://www.fraca7.net/TaskCoach-packages/TaskCoach-r%s-1.src.rpm' % self.getProperty('got_revision'))

        cname = '/var/www/htdocs/TaskCoach-packages/TaskCoach-latest-1.noarch.rpm'
        if os.path.exists(cname):
            os.remove(cname)
        os.symlink('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s-1.noarch.rpm' % self.getProperty('got_revision'),
                   cname)

        cname = '/var/www/htdocs/TaskCoach-packages/TaskCoach-latest-1.src.rpm'
        if os.path.exists(cname):
            os.remove(cname)
        os.symlink('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s-1.src.rpm' % self.getProperty('got_revision'),
                   cname)

class UploadRPM(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/TaskCoach-r%s-1.noarch.rpm', 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s-1.noarch.rpm', 'got_revision')
        kwargs['mode'] = 0644
        FileUpload.__init__(self, **kwargs)

class UploadSRPM(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/TaskCoach-r%s-1.src.rpm', 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s-1.src.rpm', 'got_revision')
        kwargs['mode'] = 0644
        FileUpload.__init__(self, **kwargs)

class BuildFedoraBase(DistCompile):
    name = 'fedora'
    description = ['Generating', 'Fedora', 'package']
    descriptionDone = ['Fedora', 'package']

    def createSummary(self, log):
        # Not calling parent because there are a bunch of warnings we
        # don't really care about.
        # DistCompile.createSummary(self, log)
        self.addURL('download',
                    'http://www.fraca7.net/TaskCoach-packages/taskcoach-r%s-1.fc%d.noarch.rpm' % (self.getProperty('got_revision'),
                                                                                                  self.fedoraVersion))

        cname = '/var/www/htdocs/TaskCoach-packages/taskcoach-latest-1.fc%d.noarch.rpm' % self.fedoraVersion
        if os.path.exists(cname):
            os.remove(cname)
        os.symlink('/var/www/htdocs/TaskCoach-packages/taskcoach-r%s-1.fc%d.noarch.rpm' % (self.getProperty('got_revision'),
                                                                                           self.fedoraVersion),
                   cname)

class UploadFedoraBase(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/taskcoach-r%%s-1.fc%d.noarch.rpm' % self.fedoraVersion, 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-packages/taskcoach-r%%s-1.fc%d.noarch.rpm' % self.fedoraVersion, 'got_revision')
        kwargs['mode'] = 0644
        FileUpload.__init__(self, **kwargs)

class BuildFedora8(BuildFedoraBase):
    fedoraVersion = 8

class BuildFedora11(BuildFedoraBase):
    fedoraVersion = 11

class UploadFedora8(UploadFedoraBase):
    fedoraVersion = 8

class UploadFedora11(UploadFedoraBase):
    fedoraVersion = 11
