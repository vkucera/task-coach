import wx, gui.viewer

def viewer2csv(viewer):
    visibleColumns = viewer.visibleColumns()
    csvRows = [[column.header() for column in visibleColumns]]
    tree = viewer.isTreeViewer()
    for item in viewer.visibleItems():
        row = [column.render(item) for column in visibleColumns]
        if tree:
            indentLevel = len(item.ancestors())
            row[0] = ' ' * indentLevel + row[0]
        csvRows.append(row)
    return csvRows
 