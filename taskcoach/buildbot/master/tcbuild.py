#!/usr/bin/python

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

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


from buildbot.steps.shell import Compile, WithProperties
from buildbot.steps.transfer import FileUpload, DirectoryUpload
from buildbot import interfaces
from buildbot.process.buildstep import SUCCESS, FAILURE

from twisted.python import log

from zope.interface import implements


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


class Revision(Compile):
    name = 'Revision'
    description = ['Generating', 'revision', 'file']
    descriptionDone = ['Revision', 'file', 'generated']

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'revision', WithProperties('TCVERSION=%s',
                                                                'got_revision')]
        Compile.__init__(self, **kwargs)


#==============================================================================
# Tests and documentation

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
        # Same remark as for UnitTests
        kwargs['haltOnFailure'] = False
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
    warningPattern = '.*Warning:.*'

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'epydoc']
        Compile.__init__(self, **kwargs)

    def createSummary(self, log):
        Compile.createSummary(self, log)

        self.addURL('Documentation',
                    'http://www.fraca7.net/TaskCoach-doc/%s/index.html' % (self.getProperty('buildername')))


class UploadDoc(DirectoryUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = 'epydoc.out'
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-doc/%s',
                                              'buildername')
        kwargs['mode'] = 0755
        kwargs['compress'] = None
        DirectoryUpload.__init__(self, **kwargs)



#==============================================================================
# Platform-specific packages

class DistCompile(Compile):
    def __init__(self, **kwargs):
        kwargs['command'] = ['make', self.name,
                             WithProperties('TCVERSION=r%s', 'got_revision')]
        Compile.__init__(self, **kwargs)

    def createSummary(self, log):
        url = 'http://www.fraca7.net/TaskCoach-packages/%%s/%s' % self.filename()
        url = url % (self.getProperty('branch') or '', self.getProperty('got_revision'))

        self.addURL('Download', url)


class UploadBase(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/%s' % self.filename(), 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-packages/%%s/%s' % self.filename(),
                                              'branch', 'got_revision')
        kwargs['mode'] = 0644
        FileUpload.__init__(self, **kwargs)

# Mac OS X

class DMGMixin:
    def filename(self):
        return 'TaskCoach-r%s.dmg'

class BuildDMG(DistCompile, DMGMixin):
    name = 'dmg'
    description = ['Generating', 'MacOS', 'binary']
    descriptionDone = ['MacOS', 'binary']


class UploadDMG(UploadBase, DMGMixin):
    pass

# Windows

class EXEMixin:
    def filename(self):
        return 'TaskCoach-r%s-win32.exe'

class BuildEXE(DistCompile, EXEMixin):
    name = 'windist'
    description = ['Generating', 'Windows', 'binary']
    descriptionDone = ['Windows', 'binary']


class UploadEXE(UploadBase, EXEMixin):
    pass

# Source

class BuildSource(DistCompile):
    name = 'sdist'
    description = ['Generating', 'source', 'distribution']
    descriptionDone = ['Source', 'distribution']

    def createSummary(self, log):
        # Special case, handle this ourselves
        # DistCompile.createSummary(self, log)

        self.addURL('download .tar.gz',
                    'http://www.fraca7.net/TaskCoach-packages/%s/TaskCoach-r%s.tar.gz' % (self.getProperty('branch') or '',
                                                                                          self.getProperty('got_revision')))
        self.addURL('download .zip',
                    'http://www.fraca7.net/TaskCoach-packages/%s/TaskCoach-r%s.zip' % (self.getProperty('branch') or '',
                                                                                       self.getProperty('got_revision')))


class UploadSourceTar(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/TaskCoach-r%s.tar.gz', 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-packages/%s/TaskCoach-r%s.tar.gz', 'branch', 'got_revision')
        kwargs['mode'] = 0644
        FileUpload.__init__(self, **kwargs)


class UploadSourceZip(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/TaskCoach-r%s.zip', 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/%s/TaskCoach-packages/TaskCoach-r%s.zip', 'branch', 'got_revision')
        kwargs['mode'] = 0644
        FileUpload.__init__(self, **kwargs)

# Debian

class DEBMixin:
    def filename(self):
        return 'taskcoach_r%s-1_all.deb'


class BuildDEB(DistCompile, DEBMixin):
    name = 'deb'
    description = ['Generating', 'Debian', 'package']
    descriptionDone = ['Debian', 'package']


class UploadDEB(UploadBase, DEBMixin):
    pass

# Generic RPM

class BuildRPM(DistCompile):
    name = 'rpm'
    description = ['Generating', 'RPM', 'package']
    descriptiondone = ['RPM', 'package']

    def createSummary(self, log):
        # Not calling parent because there are a bunch of warnings we
        # don't really care about.
        # DistCompile.createSummary(self, log)
        self.addURL('download',
                    'http://www.fraca7.net/TaskCoach-packages/%s/TaskCoach-r%s-1.noarch.rpm' % (self.getProperty('branch') or '',
                                                                                                self.getProperty('got_revision')))

        self.addURL('download',
                    'http://www.fraca7.net/TaskCoach-packages/%s/TaskCoach-r%s-1.src.rpm' % (self.getProperty('branch') or '',
                                                                                             self.getProperty('got_revision')))


class UploadRPM(UploadBase):
    def filename(self):
        return 'TaskCoach-r%s-1.noarch.rpm'


class UploadSRPM(UploadBase):
    def filename(self):
        return 'TaskCoach-r%s-1.src.rpm'

# Fedora

class FedoraMixin:
    def filename(self):
        return 'taskcoach-r%%s-1.fc%d.noarch.rpm' % self.fedoraVersion


class BuildFedoraBase(DistCompile, FedoraMixin):
    name = 'fedora'
    description = ['Generating', 'Fedora', 'package']
    descriptionDone = ['Fedora', 'package']


class UploadFedoraBase(UploadBase, FedoraMixin):
    pass


class BuildFedora8(BuildFedoraBase):
    fedoraVersion = 8


class BuildFedora11(BuildFedoraBase):
    fedoraVersion = 11


class UploadFedora8(UploadFedoraBase):
    fedoraVersion = 8


class UploadFedora11(UploadFedoraBase):
    fedoraVersion = 11
