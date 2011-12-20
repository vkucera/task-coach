#!/usr/bin/python

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
