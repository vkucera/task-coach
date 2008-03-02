'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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
    htmlText = '<html>\n<head><meta http-equiv="Content-Type" content="text/html;charset=utf-8"></head>\n<body><table border=1 cellpadding=2>\n'
    columnAlignments = [{wx.LIST_FORMAT_LEFT: 'left',
                         wx.LIST_FORMAT_CENTRE: 'center',
                         wx.LIST_FORMAT_RIGHT: 'right'}[column.alignment()]
                         for column in visibleColumns]
    htmlText += '<tr>'
    for column, alignment in zip(visibleColumns, columnAlignments):
        htmlText += '<th align="%s">%s</th>'%(alignment, column.header())
    htmlText += '</tr>\n'
    tree = viewer.isTreeViewer()
    if selectionOnly:
        selection = viewer.curselection()
        if tree:
            selection = extendedWithAncestors(selection)
    for item in viewer.visibleItems():
        if selectionOnly and item not in selection:
            continue
        bgColor = viewer.getBackgroundColor(item)
        if bgColor:
            try:
                bgColor = bgColor.GetAsString(wx.C2S_HTML_SYNTAX)
            except AttributeError: # bgColor is a tuple
                bgColor = wx.Color(*bgColor).GetAsString(wx.C2S_HTML_SYNTAX)
            htmlText += '<tr bgcolor="%s">'%bgColor
        else:
            htmlText += '<tr>'
        if tree:
            space = '&nbsp;' * len(item.ancestors()) * 3
        else:
            space = ''
        color = viewer.getColor(item)
        
        htmlText += '<td align="%s">%s%s</td>'%(columnAlignments[0], space,
            render(item, visibleColumns[0], color))
        for column, alignment in zip(visibleColumns[1:], columnAlignments[1:]):
            htmlText += '<td align="%s">%s</td>'%(alignment,
                render(item, column, color))
        htmlText += '</tr>\n'
    htmlText += '</table></body></html>\n'
    return htmlText


def render(item, column, color):
    if color[:3] != (0, 0, 0):
        color = '#%02X%02X%02X'%(color[0], color[1], color[2])
        return '<font color="%s">%s</font>'%(color, column.render(item))
    else:
        return column.render(item)
    

def extendedWithAncestors(selection):
    extendedSelection = selection[:]
    for item in selection:
        for ancestor in item.ancestors():
            if ancestor not in extendedSelection:
                extendedSelection.append(ancestor)
    return extendedSelection
