import wx

def viewer2html(viewer):
    visibleColumns = viewer.visibleColumns()
    htmlText = '<html><body><table>\n'
    columnAlignments = [{wx.LIST_FORMAT_LEFT: 'left',
                         wx.LIST_FORMAT_CENTRE: 'center',
                         wx.LIST_FORMAT_RIGHT: 'right'}[column.alignment()]
                         for column in visibleColumns]
    htmlText += '<tr>'
    for column, alignment in zip(visibleColumns, columnAlignments):
        htmlText += '<th align="%s">%s</th>'%(alignment, column.header())
    htmlText += '</tr>\n'
    for item in viewer.model():
        htmlText += '<tr>'
        for column, alignment in zip(visibleColumns, columnAlignments):
            htmlText += '<td align="%s">%s</td>'%(alignment,
                column.render(item))
        htmlText += '</tr>\n'
    htmlText += '</table></body></html>\n'
    return htmlText
 

