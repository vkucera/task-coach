#!/usr/bin/python

import os, shutil

def nuke():
    sin, sout = os.popen4('svn st --no-ignore')

    for line in sout:
        if line.startswith('?') or line.startswith('I'):
            filename = line[7:].strip()
            if filename != '.buildbot-sourcedata':
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
                print 'Removed', filename

    sout.close()
    sin.close()

if __name__ == '__main__':
    nuke()
