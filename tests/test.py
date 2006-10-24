#!/usr/bin/env python

import wxversion
wxversion.select("2.6")

import sys, unittest, os, wx, time, glob, coverage
projectRoot = os.path.abspath('..')
if projectRoot not in sys.path:
    sys.path.insert(0, projectRoot)
import taskcoach
    

class TestCase(unittest.TestCase):
    def tearDown(self):
        import patterns
        patterns.Publisher().clear()
        super(TestCase, self).tearDown()
        

class wxTestCase(TestCase):
    app = wx.App(0)
    frame = wx.Frame(None, -1, 'Frame')
    from taskcoachlib import gui
    gui.init()
        

def cvsCommit():
    os.system('cvs commit')


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
        if self._options.commit and result.wasSuccessful():
            cvsCommit()
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


import config
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

    def cvsOptionGroup(self):
        cvs = config.OptionGroup(self, 'CVS', 
            'Options to interact with CVS.')
        cvs.add_option('-c', '--commit', default=False, action='store_true', 
            help='commit if all the tests succeed'
                 ' (implies --unittests and --integrationtests)')
        return cvs

    def profileOptionGroup(self):
        profile = config.OptionGroup(self, 'Profiling', 
            'Options to profile the tests to see what test code or production '
            'code is taking the most time. Each of these options implies '
            '--no-commit and --no-coverage.')
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
        if options.profile or args:
            options.commit = False
        if options.profile:
            options.coverage = False
        if options.commit:
            options.unittests = True
            options.integrationtests = True
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
        allTests.runTests()
