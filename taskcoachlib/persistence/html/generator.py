import wx

def viewer2html(viewer, selectionOnly=False):
    visibleColumns = viewer.visibleColumns()
    htmlText = '<html>\n<head><meta http-equiv="Content-Type" content="text/html;charset=utf-8"></head>\n<body><table border=1>\n'
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
            except AttributeError:
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
