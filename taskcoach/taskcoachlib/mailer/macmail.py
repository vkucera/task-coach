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

from taskcoachlib.i18n import _


def getSubjectOfMail(messageId): # pylint: disable=W0613
    """This should return the subject of the mail having the specified
    message-id. Unfortunately, until I find an Applescript guru, it
    will only return the subject of the currently selected mail in
    Mail.app."""

    """script = '''
tell application "Mail"
    set theMessages to selection
    subject of beginning of theMessages
end tell
'''

    wx.SetCursor(wx.HOURGLASS_CURSOR)
    try:
        sp = subprocess.Popen('osascript', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = sp.communicate(script)
    finally:
        wx.SetCursor(wx.STANDARD_CURSOR)

    if sp.returncode:
        return ''

    return out.strip()""" # pylint: disable=W0105

    # The above code is slow, wrong and dangerous. I'll try to fix it some day.

    return _('Mail.app message')

