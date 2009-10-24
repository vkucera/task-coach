'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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

import os, atexit, tempfile
from taskcoachlib import patterns

class TempFiles(object):
    __metaclass__ = patterns.Singleton
    
    def __init__(self):
        self.__tempFiles = []
        atexit.register(self.cleanup)
        
    def register(self, filename):
        # Keep an open handle to the file. Under Windows, this
        # prevents the user from deleting it. I couldn't find a
        # way to prevent deletion of a file under Linux without
        # preventing read access; on the other hand few Linux
        # users clean up their temp dir themselves...
        fp = file(filename, 'rb')
        self.__tempFiles.append((fp, filename))

    def cleanup(self):
        for fp, name in self.__tempFiles:
            fp.close()
            try:
                os.remove(name)
            except:
                pass # pylint: disable-msg=W0702


def get_temp_file(**kwargs):
    ''' Return the name of a temporary file. This file will be registered
        for deletion at process termination. '''

    fd, filename = tempfile.mkstemp(**kwargs)
    os.close(fd)
    TempFiles().register(filename)
    return filename

