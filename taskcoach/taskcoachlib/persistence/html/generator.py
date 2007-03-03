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
        htmlText += '<tr>'
        if tree:
            space = '&nbsp;' * len(item.ancestors()) * 3
        else:
            space = ''
        htmlText += '<td align="%s">%s%s</td>'%(columnAlignments[0], space,
            visibleColumns[0].render(item))
        for column, alignment in zip(visibleColumns[1:], columnAlignments[1:]):
            htmlText += '<td align="%s">%s</td>'%(alignment,
                column.render(item))
        htmlText += '</tr>\n'
    htmlText += '</table></body></html>\n'
    return htmlText
 
def extendedWithAncestors(selection):
    extendedSelection = selection[:]
    for item in selection:
        for ancestor in item.ancestors():
            if ancestor not in extendedSelection:
                extendedSelection.append(ancestor)
    return extendedSelection
