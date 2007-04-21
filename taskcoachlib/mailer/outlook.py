
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
            sel.Item(n).SaveAs(filename, 0)
            ret.append(filename)

        return ret
