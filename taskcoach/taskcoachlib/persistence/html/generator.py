import wx, gui.viewer

def viewer2html(viewer):
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
    htmlText += model2html(viewer.model(), visibleColumns, columnAlignments)
    htmlText += '</table></body></html>\n'
    return htmlText
 
def listModel2html(model, visibleColumns, columnAlignments):
    htmlText = ''
    for item in model:
        htmlText += '<tr>'
        for column, alignment in zip(visibleColumns, columnAlignments):
            htmlText += '<td align="%s">%s</td>'%(alignment,
                column.render(item))
        htmlText += '</tr>\n'
    return htmlText

def treeModel2html(model, visibleColumns, columnAlignments):
    htmlText = ''
    for item in model.rootItems(): # Note: we assume a tree consists of tasks
        htmlText += node2html(item, visibleColumns, columnAlignments)
    return htmlText

def node2html(item, visibleColumns, columnAlignments, level=0):
    htmlText = '<tr>'
    for column, alignment in zip(visibleColumns, columnAlignments):
        space = '&nbsp;' * level * 3
        htmlText += '<td align="%s">%s%s</td>'%(alignment, space, 
            column.render(item))
    htmlText += '</tr>\n'
    for child in item.children():
        htmlText += node2html(child, visibleColumns, columnAlignments, level+1)
    return htmlText
