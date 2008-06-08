#!/usr/bin/env python

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007 Jerome Laheurte <fraca7@free.fr>

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

import sys, os
if not hasattr(sys, "frozen"):
    # These checks are only necessary in a non-frozen environment, i.e. we
    # skip these checks when run from a py2exe-fied application
    import wxversion
    try:
        wxversion.ensureMinimal("2.8-unicode", optionsRequired=True)
    except:
        pass
    try:
        import taskcoachlib
    except ImportError:
        sys.stderr.write('''ERROR: cannot import the library 'taskcoachlib'.
Please see http://www.taskcoach.org/faq.html for more information and
possible resolutions.''')
        sys.exit(1)

    if sys.platform == 'linux2':
        sys.path.insert(0, os.path.join(os.getcwd(), 'bin.in', 'linux'))
    elif sys.platform == 'darwin':
        sys.path.insert(0, os.path.join(os.getcwd(), 'bin.in', 'macos'))
    else:
        sys.path.insert(0, os.path.join(os.getcwd(), 'bin.in', 'windows'))

def start():
    from taskcoachlib import config, application
    options, args = config.ApplicationOptionParser().parse_args()
    app = application.Application(options, args)
    if options.profile:
        import hotshot
        profiler = hotshot.Profile('.profile')
        profiler.runcall(app.start)
    else:
        app.start()


if __name__ == '__main__':
    start()
