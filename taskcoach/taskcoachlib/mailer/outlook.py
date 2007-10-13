
import os, tempfile

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
                # Add Outlook internal ID as custom header...
                name = tempfile.mktemp('.eml')
                src = file(filename, 'rb')
                try:
                    dst = file(name, 'wb')
                    try:
                        s = 0
                        for line in src:
                            if s == 0:
                                if line.strip() == '':
                                    dst.write('X-Outlook-ID: %s\r\n' % str(sel.Item(n).EntryID))
                                    s = 1
                            dst.write(line)
                    finally:
                        dst.close()
                finally:
                    src.close()
                ret.append(name)
            finally:
                os.remove(filename)

        return ret
