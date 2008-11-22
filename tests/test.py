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

import sys, unittest, os, time, glob, coverage, wx
projectRoot = os.path.abspath('..')
if projectRoot not in sys.path:
    sys.path.insert(0, projectRoot)

class TestCase(unittest.TestCase):
    def assertEqualLists(self, expectedList, actualList):
        self.assertEqual(len(expectedList), len(actualList))
        for item in expectedList:
            self.failUnless(item in actualList)
            
    def registerObserver(self, eventType):
        if not hasattr(self, 'events'):
            self.events = []
        from taskcoachlib import patterns
        patterns.Publisher().registerObserver(self.onEvent, eventType=eventType)
        
    def onEvent(self, event):
        self.events.append(event)

    def tearDown(self):
        # Prevent processing of pending events after the test has finished:
        wx.GetApp().Disconnect(wx.ID_ANY) 
        from taskcoachlib import patterns
        patterns.Publisher().clear()
        patterns.CommandHistory().clear()
        patterns.NumberedInstances.count = dict()
        from taskcoachlib.domain import date
        date.Clock().reset()
        if hasattr(self, 'events'):
            del self.events
        super(TestCase, self).tearDown()
        

class wxTestCase(TestCase):
    app = wx.App(0)
    frame = wx.Frame(None, -1, 'Frame')
    from taskcoachlib import gui
    gui.init()

    def setUp(self):
        pass

    def tearDown(self):
        super(wxTestCase, self).tearDown()
        self.frame.DestroyChildren() # Clean up GDI objects on Windows


class TestResultWithTimings(unittest._TextTestResult):
    def __init__(self, *args, **kwargs):
        super(TestResultWithTimings, self).__init__(*args, **kwargs)
        self._timings = {}

    def startTest(self, test):
        super(TestResultWithTimings, self).startTest(test)
        self._timings[test] = time.time()
        
    def stopTest(self, test):
        super(TestResultWithTimings, self).stopTest(test)
        self._timings[test] = time.time() - self._timings[test]


class TextTestRunnerWithTimings(unittest.TextTestRunner):
    def __init__(self, nrTestsToReport, timeTests=False, *args, **kwargs):
        super(TextTestRunnerWithTimings, self).__init__(*args, **kwargs)
        self._timeTests = timeTests
        self._nrTestsToReport = nrTestsToReport

    def _makeResult(self):
        return TestResultWithTimings(self.stream, self.descriptions, 
            self.verbosity)

    def run(self, *args, **kwargs):
        result = super(TextTestRunnerWithTimings, self).run(*args, **kwargs)
        if self._timeTests:
            sortableTimings = [(time, test) for test, time in result._timings.items()]
            sortableTimings.sort(reverse=True)
            print '\n%d slowest tests:'%self._nrTestsToReport
            for time, test in sortableTimings[:self._nrTestsToReport]:
                print '%s (%.2f)'%(test, time)
        return result


class AllTests(unittest.TestSuite):
    def __init__(self, options, testFiles=None):
        super(AllTests, self).__init__()
        self._options = options 
        self.loadAllTests(testFiles or [])

    def filenameToModuleName(self, filename):
        if filename == os.path.abspath(filename):
            # Strip current working directory to get the relative path:
            filename = filename[len(os.getcwd() + os.sep):]
        module = filename.replace(os.sep, '.')
        module = module.replace('/', '.')  
        return module[:-3] # strip '.py'

    def loadAllTests(self, testFiles):
        testloader = unittest.TestLoader()
        if not testFiles:
            testfiles = []
            if self._options.unittests:
                testFiles.extend(self.getTestFilesFromDir('unittests'))
            if self._options.integrationtests:
                testFiles.extend(self.getTestFilesFromDir('integrationtests'))
            if self._options.releasetests:
                testFiles.extend(self.getTestFilesFromDir('releasetests'))
            if self._options.disttests:
                path = os.path.join('disttests', sys.platform)
                if os.path.exists(path):
                    testFiles.extend(self.getTestFilesFromDir(path))
                else:
                    print 'WARNING: no disttest for your platform (%s)' % sys.platform
        for filename in testFiles:
            moduleName = self.filenameToModuleName(filename)
            # Importing the module is not strictly necessary because
            # loadTestsFromName will do that too as a side effect. But if the 
            # test module contains errors our import will raise an exception
            # while loadTestsFromName ignores exceptions when importing from 
            # modules.
            module = __import__(moduleName)
            suite = testloader.loadTestsFromName(moduleName)
            self.addTests(suite._tests)
   
    def runTests(self):       
        testrunner = TextTestRunnerWithTimings(
            verbosity=self._options.verbosity,
            timeTests=self._options.time,
            nrTestsToReport=self._options.time_reports)
        if self._options.coverage:
            coverage.erase()
            coverage.start()
        result = testrunner.run(self)
        if self._options.coverage:
            coverage.stop()
            print coverage.report(self.getPyFilesFromDir(os.path.join(projectRoot, 
                'taskcoachlib')))
        return result

    @staticmethod
    def getPyFilesFromDir(directory):
        return AllTests.getFilesFromDir(directory, '.py')

    @staticmethod
    def getTestFilesFromDir(directory):
        return AllTests.getFilesFromDir(directory, 'Test.py')

    @staticmethod
    def getFilesFromDir(directory, extension):
        result = []
        for root, dirs, files in os.walk(directory):
            result.extend([os.path.join(root, file) for file in files \
                           if file.endswith(extension)])
            if 'CVS' in dirs:
                dirs.remove('CVS')
        return result


from taskcoachlib import config
class TestOptionParser(config.OptionParser):
    def __init__(self):
        super(TestOptionParser, self).__init__(usage='usage: %prog [options] [testfiles]')

    def testoutputOptionGroup(self):
        testoutput = config.OptionGroup(self, 'Test output',
            'Options to determine the amount of output while running the '
            'tests.')
        testoutput.add_option('-q', '--quiet', action='store_const', default=1,
            const=0, dest='verbosity', help='show only the final test result')
        testoutput.add_option('--progress', action='store_const', const=1,
            dest='verbosity', help='show progress [default]')
        testoutput.add_option('-v', '--verbose', action='store_const',
            const=2, dest='verbosity', help='show all tests')
        testoutput.add_option('-t', '--time', default=False, 
            action='store_true', 
            help='time the tests and report the slowest tests')
        testoutput.add_option('--time-reports', default=10, type='int',
            help='the number of slow tests to report [%default]')
        return testoutput

    def profileOptionGroup(self):
        profile = config.OptionGroup(self, 'Profiling', 
            'Options to profile the tests to see what test code or production '
            'code is taking the most time. Each of these options implies '
            '--no-coverage.')
        profile.add_option('-p', '--profile', default=False, 
            action='store_true', help='profile the running of all the tests')
        profile.add_option('-r', '--report-only', dest='profile_report_only', 
            action='store_true', default=False,
            help="don't make a new profile, report only on the last profile")
        profile.add_option('-s', '--sort', dest='profile_sort', 
            action='append', default=[],
            help="sort key to be used for reporting the profile data. "
            "Possible sort keys are: 'calls', 'cumulative' [default], "
            "'file', 'line', 'module', 'name', 'nfl', 'pcalls', 'stdname', "
            "and 'time'. This option may be repeated")
        profile.add_option('--callers', dest='profile_callers',
            default=False, action='store_true', help='print callers')
        profile.add_option('--callees', dest='profile_callees',
            default=False, action='store_true', help='print callees')
        profile.add_option('-l', '--limit', dest='profile_limit', default=50, 
            type="int", help="limit the number of calls to show in the "
            "profile reports [%default]")
        profile.add_option('--regex', dest='profile_regex',
            help='Regular expression to limit the functions shown in the '
           'profile reports')
        return profile

    def testselectionOptionGroup(self):
        testselection = config.OptionGroup(self, 'Test selection',
            'Options to determine which tests to run.')

        testselection.add_option('--unittests', default=True,
            action='store_true', help='run the unit tests [default]')
        testselection.add_option('--no-unittests', action='store_false', 
            help="don't run the unit tests", dest='unittests')

        testselection.add_option('--integrationtests', default=False,
            action='store_true', help='run the integration tests')
        testselection.add_option('--no-integrationtests', action='store_false', 
            help="don't run the integration tests [default]",
            dest='integrationtests')

        testselection.add_option('--releasetests', default=False,
            action='store_true', help='run the release tests')
        testselection.add_option('--no-releasetests', action='store_false', 
            help="don't run the release tests [default]", dest='releasetests')

        testselection.add_option('--disttests', default=False,
            action='store_true', help='Run the platform-specific package tests',
            dest='disttests')

        testselection.add_option('--alltests', default=False,
            action='store_true', help='run all tests')
        return testselection

    def testcoverageOptionGroup(self):
        testcoverage = config.OptionGroup(self, 'Test coverage',
            'Options to measure test (statement) coverage.')
        testcoverage.add_option('--coverage', default=False,
            action='store_true', help='measure test statement coverage')
        return testcoverage
        
    def parse_args(self):
        options, args = super(TestOptionParser, self).parse_args()
        if options.profile_report_only:
            options.profile = True
        if not options.profile_sort:
            options.profile_sort.append('cumulative')
        if options.alltests:
            options.unittests = True
            options.integrationtests = True
            options.releasetests = True
            options.disttests = True
        if options.profile:
            options.coverage = False
        return options, args


class TestProfiler:
    def __init__(self, options, logfile='.profile'):
        self._logfile = logfile
        self._options = options

    def reportLastRun(self):
        import hotshot.stats
        stats = hotshot.stats.load(self._logfile)
        stats.strip_dirs()
        for sortKey in self._options.profile_sort:
            stats.sort_stats(sortKey)
            stats.print_stats(self._options.profile_regex, 
                self._options.profile_limit)
        if self._options.profile_callers:
            stats.print_callers()
        if self._options.profile_callees:
            stats.print_callees()

    def run(self, command, *args, **kwargs):
        if self._options.profile_report_only or self.profile(command, *args, **kwargs):
            self.reportLastRun()

    def profile(self, command, *args, **kwargs):
        import hotshot
        profiler = hotshot.Profile(self._logfile)
        result = profiler.runcall(command, *args, **kwargs)
        if not result.wasSuccessful():
            self.cleanup()
        return result.wasSuccessful()
            
    def cleanup(self):
        import os
        os.remove(self._logfile)

    
if __name__ == '__main__':
    options, testFiles = TestOptionParser().parse_args()
    allTests = AllTests(options, testFiles)
    if options.profile:
        TestProfiler(options).run(allTests.runTests)
    else:
        result = allTests.runTests()
        if not result.wasSuccessful():
            sys.exit(1)
