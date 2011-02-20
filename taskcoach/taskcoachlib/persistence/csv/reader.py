'''
Task Coach - Your friendly task manager
Copyright (C) 2011 Task Coach developers <developers@taskcoach.org>

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


import StringIO


def splitLines(text, separator=','):
    """Split values delimited by a separator.

    @param separator: The separator character. If part of a value, the value must
        be enclosed in double quotes; double quotes inside the value must be
        doubled.
    """

    state = 0 # Start of value
    inQuote = False
    lines = []
    values = []
    currentValue = StringIO.StringIO()

    for character in text:
        if state == 0:
            if character == '"':
                inQuote = True
            else:
                inQuote = False
                currentValue.write(character)
            state = 1 # Reading value
        elif state == 1:
            if inQuote:
                if character == '"':
                    state = 2 # Maybe escaping
                else:
                    currentValue.write(character)
            else:
                if character == separator:
                    values.append(currentValue.getvalue())
                    currentValue = StringIO.StringIO()
                    state = 0
                elif character == '\n':
                    values.append(currentValue.getvalue())
                    lines.append(values)
                    currentValue = StringIO.StringIO()
                    values = []
                    state = 0
                elif character == '\r':
                    state = 3
                else:
                    currentValue.write(character)
        elif state == 2:
            if character == '"':
                currentValue.write(character)
                state = 1
            elif character == separator:
                values.append(currentValue.getvalue())
                currentValue = StringIO.StringIO()
                state = 0
            else:
                raise ValueError(u'Unexpected character "%s" in line "%s"' % (character, line))
        elif state == 3:
            if character == '\n':
                values.append(currentValue.getvalue())
                lines.append(values)
                currentValue = StringIO.StringIO()
                values = []
                state = 0
            else:
                currentValue.write('\r')
                currentValue.write(character)
                state = 1

    if state in [1, 2, 3] and values:
        values.append(currentValue.getvalue())
        lines.append(values)

    return lines
