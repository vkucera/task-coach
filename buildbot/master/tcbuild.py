#!/usr/bin/python

from buildbot.steps.shell import Compile
from buildbot.steps.transfer import FileUpload

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

PKGVER = '0.71.2'

class BuildDMG(Compile):
    name = 'dmg'
    description = ['Generating', 'MacOS', 'binary']
    descriptionDone = ['MacOS', 'binary']

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'dmg']
        Compile.__init__(self, **kwargs)

class BuildEXE(Compile):
    name = 'exe'
    description = ['Generating', 'Windows', 'binary']
    descriptionDone = ['Windows', 'binary']

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'windist']
        Compile.__init__(self, **kwargs)

class UploadEXE(FileUpload):
    def __init__(self, **kwargs):
        kwargs['slavesrc'] = 'dist/TaskCoach-%s-win32.exe' % PKGVER
        kwargs['masterdest'] = '~/TaskCoach-packages'
        FileUpload.__init__(self, **kwargs)

    def createSummary(self, log):
        self.addURL('download', 'http://www.fraca7.net/TaskCoach-packages/TaskCoach-%s-win32.exe' % PKGVER)

class BuildDEB(Compile):
    name = 'deb'
    description = ['Generating', 'Debian', 'package']
    descriptionDone = ['Debian', 'package']

    def __init__(self, **kwargs):
        kwargs['command'] = ['make', 'deb']
        Compile.__init__(self, **kwargs)
