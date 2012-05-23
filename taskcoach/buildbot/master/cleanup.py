#!/usr/bin/python

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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

import os, re


def cleanup(path, rx):
    files = []
    for name in os.listdir(path):
        mt = rx.search(name)
        if mt:
            files.append((int(mt.group(1)), name))
    files.sort()

    if files:
        for rev, name in files[:-1]:
            os.remove(os.path.join(path, name))


if __name__ == '__main__':
    for path in ['.', 'branches/Release1_3_Branch']:
        for rx in [r'taskcoach_\d+\.\d+\.\d+\.(\d+)-1_py26.deb',
                   r'taskcoach_\d+\.\d+\.\d+\.(\d+)-1_py25.deb',
                   r'taskcoach_\d+\.\d+\.\d+\.(\d+)-1.deb',
                   r'taskcoach-\d+\.\d+\.\d+\.(\d+)-1.fc14.noarch.rpm',
                   r'TaskCoach-\d+\.\d+\.\d+\.(\d+).zip',
                   r'TaskCoach-\d+\.\d+\.\d+\.(\d+).tar.gz',
                   r'TaskCoach-\d+\.\d+\.\d+\.(\d+).dmg',
                   r'TaskCoach-\d+\.\d+\.\d+\.(\d+)-win32.exe',
                   r'TaskCoach-\d+\.\d+\.\d+\.(\d+)-1.src.rpm',
                   r'TaskCoach-\d+\.\d+\.\d+\.(\d+)-1.noarch.rpm',
                   r'TaskCoachPortable_\d+\.\d+\.\d+\.(\d+).paf.exe',
                   r'X-TaskCoach_\d+\.\d+\.\d+\.(\d+)_rev1.zip']:
            cleanup(path, re.compile(rx))
