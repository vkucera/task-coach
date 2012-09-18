#!/usr/bin/python

# Cleanup the htdocs subdirectory where the buildbot stores the
# distribution files (only keep 2 latest versions). Run from cron.

import os, re

def cleanup(path, rx):
    files = []
    for name in os.listdir(path):
        mt = rx.search(name)
        if mt:
            files.append((int(mt.group(1)), name))

    if len(files) <= 2:
        return

    files.sort()
    files.reverse()

    for rev, name in files[2:]:
        os.remove(os.path.join(path, name))


def main(path):
    for suffix in [r'-win32\.exe', r'\.dmg', r'\.tar\.gz', r'\.zip']:
        cleanup(path, re.compile(r'^TaskCoach-r(\d+)' + suffix + '$'))
    cleanup(path, re.compile(r'taskcoach_r(\d+)-1_all\.deb'))

if __name__ == '__main__':
    main('/var/www/htdocs/TaskCoach-packages')
