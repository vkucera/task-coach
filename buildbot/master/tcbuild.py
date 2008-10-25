#!/usr/bin/python

from buildbot.steps.shell import Compile, WithProperties
from buildbot.steps.transfer import FileUpload
from buildbot import interfaces
from buildbot.process.buildstep import FAILURE
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

class UnitTests(Compile):
    name = 'unit tests'
    description = ['Running', 'unit', 'tests']
    descriptionDone = ['Unit', 'tests']

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'unittests']
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

class BuildDMG(DistCompile):
    name = 'dmg'
    description = ['Generating', 'MacOS', 'binary']
    descriptionDone = ['MacOS', 'binary']

class UploadDMG(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/TaskCoach-r%s.dmg', 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s.dmg', 'got_revision')
        FileUpload.__init__(self, **kwargs)

    def finished(self, result):
        result = FileUpload.finished(self, result)
        if result != FAILED:
            self.addURL('download',
                        WithProperties('http://www.fraca7.net/TaskCoach-packages/TaskCoach-r%s.dmg', 'got_revision'))
        return result

class BuildEXE(DistCompile):
    name = 'windist'
    description = ['Generating', 'Windows', 'binary']
    descriptionDone = ['Windows', 'binary']

class UploadEXE(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = WithProperties('dist/TaskCoach-r%s-win32.exe', 'got_revision')
        kwargs['masterdest'] = WithProperties('/var/www/htdocs/TaskCoach-packages/TaskCoach-r%s-win32.exe', 'got_revision')
        FileUpload.__init__(self, **kwargs)

    def createSummary(self, log):
        self.addURL('download',
                    WithProperties('http://www.fraca7.net/TaskCoach-packages/TaskCoach-r%s-win32.exe', 'got_revision'))

class BuildDEB(DistCompile):
    name = 'deb'
    description = ['Generating', 'Debian', 'package']
    descriptionDone = ['Debian', 'package']
