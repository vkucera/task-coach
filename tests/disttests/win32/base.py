
"""
These tests actually assume a fresh configuration (new .ini file, nothing changed).
"""

import os, time, re, unittest
import win32process, win32event, win32gui


class Win32TestCase(unittest.TestCase):
    def setUp(self):
        self.processHandle = None

        path = os.path.join('..', 'build')
        for name in os.listdir(path):
            dirname = os.path.join(path, name)
            filename = os.path.join(dirname, 'taskcoach.exe')
            if os.path.isdir(dirname) and os.path.exists(filename):
                break
        else:
            self.fail('Could not find TaskCoach executable.')

        sinfo = win32process.STARTUPINFO()
        sinfo.dwFlags = 0
        hProcess, hThread, processId, threadId = win32process.CreateProcess(filename,
                                                                            None,
                                                                            None,
                                                                            None,
                                                                            False,
                                                                            0,
                                                                            None,
                                                                            os.getcwd(),
                                                                            sinfo)
        self.processHandle = hProcess
        if win32event.WaitForInputIdle(hProcess, 10000) == win32event.WAIT_TIMEOUT:
            self.fail('Could not launch TaskCoach.')

    def tearDown(self):
        if self.processHandle is not None:
            win32process.TerminateProcess(self.processHandle, 0)

    def expectWindow(self, title, tries=10):
        """Waits for a window to appear, and return a handle to it, or
        fail the test.

        @param title: Criterion for the window's title
            (regular expression string)
        @param tries: Max number of scans to perform. Scans are one
            second apart."""

        rx = re.compile(title)

        for idx in xrange(tries):
            time.sleep(1)

            windows = []

            def enumCb(hwnd, lparam):
                try:
                    if rx.search(win32gui.GetWindowText(hwnd)):
                        windows.append(hwnd)
                except:
                    pass
                return True

            win32gui.EnumWindows(enumCb, None)

            if windows:
                return windows[0]

        self.fail('Could not find window %s.' % title)
