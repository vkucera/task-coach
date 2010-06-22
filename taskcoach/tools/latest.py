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

import os, re

def findLatest(path, valid):
    rx = re.compile('(.*)r(\d+)(.*)')

    results = dict()

    for name in os.listdir(path):
        if name.lower().startswith('taskcoach') and valid(name):
            mt = rx.search(name)
            if mt:
                ls = results.get((mt.group(1), mt.group(3)), [])
                ls.append(int(mt.group(2)))
                results[(mt.group(1), mt.group(3))] = ls

    packages = []

    for (part1, part3), versions in results.items():
        versions.sort()
        packages.append('%sr%d%s' % (part1, versions[-1], part3))

    packages.sort()

    return packages


def listPath(path):
    def isSource(name):
	return name.endswith('.zip') or name.endswith('.tar.gz') or name.endswith('.src.rpm')

    print '<h2>Sources</h2>'
    print '<ul>'

    for pkgname in findLatest(path, isSource):
        print '<li><a href="http://www.fraca7.net/TaskCoach-packages/%s">%s</a></li>' % (pkgname, pkgname)

    print '</ul>'

    print '<h2>Binaries</h2>'
    print '<ul>'

    for pkgname in findLatest(path, lambda x: not isSource(x)):
        print '<li><a href="http://www.fraca7.net/TaskCoach-packages/%s">%s</a></li>' % (pkgname, pkgname)

    print '</ul>'

def main():
    print 'Content-type: text/html'
    print

    print '<html><head><title>Latest Task Coach builds</title>'
    print '<style type="text/css" media="screen">@import "default.css";</style>'
    print '</head></body>'
    print '<h1>From Trunk</h1>'
    listPath('.')

    for name in os.listdir('branches'):
        fname = os.path.join('branches', name)
        if os.path.isdir(fname):
            print '<h1>From %s</h1>' % name
            listPath(fname)

    print '<a href="http://www.taskcoach.org/download.html>Back to Task Coach downloads</a>'

    print '</body></html>'

if __name__ == '__main__':
    main()
