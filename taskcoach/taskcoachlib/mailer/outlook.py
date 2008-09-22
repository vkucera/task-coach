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

import os, tempfile
from taskcoachlib.thirdparty.desktop import get_temp_file

if os.name == 'nt':
    from win32com.client import GetActiveObject

    def getCurrentSelection():
        obj = GetActiveObject('Outlook.Application')
        exp = obj.ActiveExplorer()
        sel = exp.Selection

        ret = []
        for n in xrange(1, sel.Count + 1):
            filename = tempfile.mktemp('.eml')
            try:
                sel.Item(n).SaveAs(filename, 0)
                # Add Outlook internal ID as custom header... It seems
                # that some versions of Outlook don't put a blank line
                # between subject and headers.

                name = get_temp_file(suffix='.eml')
                src = file(filename, 'rb')
                linenb = 0

                try:
                    dst = file(name, 'wb')
                    try:
                        s = 0
                        for line in src:
                            linenb += 1
                            if s == 0:
                                if line.strip() == '' or linenb == 5:
                                    dst.write('X-Outlook-ID: %s\r\n' % str(sel.Item(n).EntryID))
                                    s = 1
                                if linenb == 5 and line.strip() != '':
                                    dst.write('\r\n')
                            dst.write(line)
                    finally:
                        dst.close()
                finally:
                    src.close()
                ret.append(name)
            finally:
                os.remove(filename)

        return ret

