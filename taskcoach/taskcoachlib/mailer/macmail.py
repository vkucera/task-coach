'''
Task Coach - Your friendly task manager
Copyright (C) 2010 Jerome Laheurte <fraca7@free.fr>

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

import subprocess

def getSubjectOfMail(messageId):
    """This should return the subject of the mail having the specified
    message-id. Unfortunately, until I find an Applescript guru, it
    will only return the subject of the currently selected mail in
    Mail.app."""

    script = '''
tell application "Mail"
    set theMessages to selection
    subject of beginning of theMessages
end tell
'''

    sp = subprocess.Popen('osascript', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = sp.communicate(script)

    if sp.returncode:
        return ''

    return out.strip()
