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
    if viewer.isTreeViewer():
        model2html = treeModel2html
    else:
        model2html = listModel2html
    htmlText += model2html(viewer.model(), visibleColumns, columnAlignments, 
                           selectionOnly, viewer.curselection())
    htmlText += '</table></body></html>\n'
    return htmlText
 
def listModel2html(model, visibleColumns, columnAlignments, selectionOnly, 
                   selection):
    htmlText = ''
    for item in model:
        if selectionOnly and item not in selection:
            continue
        htmlText += '<tr>'
        for column, alignment in zip(visibleColumns, columnAlignments):
            htmlText += '<td align="%s">%s</td>'%(alignment,
                column.render(item))
        htmlText += '</tr>\n'
    return htmlText

def treeModel2html(model, visibleColumns, columnAlignments, selectionOnly, 
                   selection):
    selection = extendedWithAncestors(selection)
    htmlText = ''
    for item in model.rootItems():
        htmlText += node2html(item, visibleColumns, columnAlignments, 
                              selectionOnly, selection)
    return htmlText

def extendedWithAncestors(selection):
    extendedSelection = selection[:]
    for item in selection:
        for ancestor in item.ancestors():
            if ancestor not in extendedSelection:
                extendedSelection.append(ancestor)
    return extendedSelection

def node2html(item, visibleColumns, columnAlignments, selectionOnly, selection, 
              level=0):
    if selectionOnly and item not in selection:
        return ''
    htmlText = '<tr>'
    for column, alignment in zip(visibleColumns, columnAlignments):
        space = '&nbsp;' * level * 3
        htmlText += '<td align="%s">%s%s</td>'%(alignment, space, 
            column.render(item))
    htmlText += '</tr>\n'
    for child in item.children():
        htmlText += node2html(child, visibleColumns, columnAlignments, 
                              selectionOnly, selection, level+1)
    return htmlText
