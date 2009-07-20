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

docType = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'
metaTag = '<meta http-equiv="Content-Type" content="text/html;charset=utf-8">'
cssLink = '<link href="%s" rel="stylesheet" type="text/css" media="screen">'
tableStartTag = '<table id="table">'


def viewer2html(viewer, cssFilename=None, selectionOnly=False):
    visibleColumns = viewer.visibleColumns()
    htmlText = '%s\n<html>\n  <head>\n    %s\n'%(docType, metaTag)
    if cssFilename:
        htmlText += '    %s\n'%(cssLink%cssFilename)
    htmlText += '  </head>\n  <body>\n    %s\n'%tableStartTag
    
    columnAlignments = [{wx.LIST_FORMAT_LEFT: 'left',
                         wx.LIST_FORMAT_CENTRE: 'center',
                         wx.LIST_FORMAT_RIGHT: 'right'}[column.alignment()]
                         for column in visibleColumns]
    indent = 6
    htmlText += ' '*indent + '<caption>%s</caption>\n'%viewer.title()
    htmlText += ' '*indent + '<thead>\n'
    indent += 2
    htmlText += ' '*indent + '<tr class="header">\n'
    indent += 2
    for column, alignment in zip(visibleColumns, columnAlignments):
        header = column.header() or '&nbsp;'
        name = column.name()
        if viewer.isSortable() and viewer.isSortedBy(name):
            id = ' id="sorted" '
        else:
            id = ''
        htmlText += ' '*indent + '<th scope="col" class="%s"%salign="%s">%s</th>\n'%(name, id, alignment, header)
    indent -= 2
    htmlText += ' '*indent + '</tr>\n'
    indent -= 2
    htmlText += ' '*indent + '</thead>\n'
    htmlText += ' '*indent + '<tbody>\n'
    indent += 2
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

        color = viewer.getColor(item)
        renderedItem = render(item, visibleColumns[0], color, tree)
        htmlText += cell(renderedItem, visibleColumns[0], columnAlignments[0], indent)
        for column, alignment in zip(visibleColumns[1:], columnAlignments[1:]):
            renderedItem = render(item, column, color)
            htmlText += cell(renderedItem, column, alignment, indent)
        htmlText += ' '*indent + '</tr>\n'
    indent -= 2
    htmlText += ' '*indent + '</tbody>\n'
    htmlText += '''    </table>
  </body>
</html>
'''
    return htmlText, count


def cell(item, column, alignment, indent):
    return ' ' * (indent+2) + '<td class="%s" align="%s">%s</td>\n'%(column.name(),
        alignment, item)


def render(item, column, color, tree=False):
    renderedItem = column.render(item)
    renderedItem = renderedItem.replace('\n', '<br>')
    if color[:3] != (0, 0, 0):
        color = '#%02X%02X%02X'%(color[0], color[1], color[2])
        renderedItem = '<font color="%s">%s</font>'%(color, renderedItem)
    if tree:
        renderedItem = '&nbsp;' * len(item.ancestors()) * 3 + renderedItem
    if not renderedItem:
        renderedItem = '&nbsp;'
    return renderedItem
    