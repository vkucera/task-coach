'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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

import wx


def viewer2html(viewer, selectionOnly=False):
    visibleColumns = viewer.visibleColumns()
    htmlText = '''<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
  </head>
  <body>
    <table border=1 cellpadding=2>
'''
    columnAlignments = [{wx.LIST_FORMAT_LEFT: 'left',
                         wx.LIST_FORMAT_CENTRE: 'center',
                         wx.LIST_FORMAT_RIGHT: 'right'}[column.alignment()]
                         for column in visibleColumns]
    indent = 6
    htmlText += ' '*indent + '<tr>\n'
    indent += 2
    for column, alignment in zip(visibleColumns, columnAlignments):
        header = column.header() or '&nbsp;'
        htmlText += ' '*indent + '<th align="%s">%s</th>\n'%(alignment, header)
    indent -= 2
    htmlText += ' '*indent + '</tr>\n'
    tree = viewer.isTreeViewer()
    count = 0
    for item in viewer.visibleItems():
        if selectionOnly and not viewer.isselected(item):
            continue
        count += 1
        bgColor = viewer.getBackgroundColor(item)
        if bgColor:
            try:
                bgColor = bgColor.GetAsString(wx.C2S_HTML_SYNTAX)
            except AttributeError: # bgColor is a tuple
                bgColor = wx.Color(*bgColor).GetAsString(wx.C2S_HTML_SYNTAX)
            htmlText += ' '*indent + '<tr bgcolor="%s">\n'%bgColor
        else:
            htmlText += ' '*indent + '<tr>\n'
        if tree:
            space = '&nbsp;' * len(item.ancestors()) * 3
        else:
            space = ''
        color = viewer.getColor(item)
        
        indent +=2
        htmlText += ' '*indent + '<td align="%s">%s%s</td>\n'%(columnAlignments[0], space,
            render(item, visibleColumns[0], color))
        for column, alignment in zip(visibleColumns[1:], columnAlignments[1:]):
            renderedItem = render(item, column, color) or '&nbsp;'
            htmlText += ' '*indent + '<td align="%s">%s</td>\n'%(alignment,
                renderedItem)
        indent -= 2
        htmlText += ' '*indent + '</tr>\n'
    htmlText += '''    </table>
  </body>
</html>
'''
    return htmlText, count


def render(item, column, color):
    renderedItem = column.render(item)
    renderedItem = renderedItem.replace('\n', '<br>')
    if color[:3] != (0, 0, 0):
        color = '#%02X%02X%02X'%(color[0], color[1], color[2])
        renderedItem = '<font color="%s">%s</font>'%(color, renderedItem)
    return renderedItem
    