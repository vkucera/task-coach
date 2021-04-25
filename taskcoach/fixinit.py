'''
Task Coach - Your friendly task manager
Copyright (C) 2012 Task Coach developers <developers@taskcoach.org>

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

import os


if __name__ == '__main__':
    for root, dirs, files in os.walk(os.path.join('taskcoachlib', 'thirdparty')):
        for name in files:
            if name != '.hg':
                filename = os.path.join(root, name)
                if name in ['__init__.py', 'itopicdefnprovider.py'] and os.stat(filename).st_size == 0:
                    with open(filename, 'w') as fileobj:
                        fileobj.write('# Not empty\n')
