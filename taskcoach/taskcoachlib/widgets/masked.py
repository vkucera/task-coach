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

import locale
from wx.lib import masked
from taskcoachlib import operating_system


class FixOverwriteSelectionMixin(object):
    def _SetSelection(self, start, end):
        if operating_system.isGTK(): # pragma: no cover
            # By exchanging the start and end parameters we make sure that the 
            # cursor is at the start of the field so that typing overwrites the 
            # current field instead of moving to the next field:
            start, end = end, start
        super(FixOverwriteSelectionMixin, self)._SetSelection(start, end)


class TextCtrl(FixOverwriteSelectionMixin, masked.TextCtrl):
    pass


class AmountCtrl(FixOverwriteSelectionMixin, masked.NumCtrl):
    def __init__(self, parent, value=0, locale_conventions=None):
        locale_conventions = locale_conventions or locale.localeconv()
        decimalChar = locale_conventions['decimal_point'] or '.'
        groupChar = locale_conventions['thousands_sep'] or ','
        groupDigits = len(locale_conventions['grouping']) > 1
        # The thousands separator may come up as ISO-8859-1 character
        # 0xa0, which looks like a space but isn't ASCII, which
        # confuses NumCtrl... Play it safe and avoid any non-ASCII
        # character here, or groupChars that consist of multiple characters.
        if len(groupChar) > 1 or ord(groupChar) >= 128:
            groupChar = ','
        # Prevent decimalChar and groupChar from being the same:
        if groupChar == decimalChar:
            groupChar = '.' if decimalChar == ',' else ','
        super(AmountCtrl, self).__init__(parent, value=value, allowNegative=False,
                                         fractionWidth=2, selectOnEntry=True,
                                         decimalChar=decimalChar, groupChar=groupChar,
                                         groupDigits=groupDigits)
        

class TimeDeltaCtrl(TextCtrl):
    def __init__(self, parent, hours, minutes, seconds, *args, **kwargs):
        mask = kwargs.pop('mask', '#{8}:##:##')
        super(TimeDeltaCtrl, self).__init__(parent, mask=mask,
            formatcodes='FS',
            fields=[masked.Field(formatcodes='r', defaultValue='%8d'%hours),
                    masked.Field(defaultValue='%02d'%minutes),
                    masked.Field(defaultValue='%02d'%seconds)], *args, **kwargs)
        
