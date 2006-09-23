import wx, gui.viewer

def viewer2csv(viewer):
    visibleColumns = viewer.visibleColumns()
    csvRows = []
    headerRow = [column.header() for column in visibleColumns]
    csvRows.append(headerRow)
    if viewer.isTreeViewer():
        model2csv = treeModel2csv
    else:
        model2csv = listModel2csv
    csvRows.extend(model2csv(viewer.model(), visibleColumns))
    return csvRows
 
def listModel2csv(model, visibleColumns):
    rows = []
    for item in model:
        rows.append([column.render(item) for column in visibleColumns])
    return rows

def treeModel2csv(model, visibleColumns):
    rows = []
    for item in model.rootItems():
        rows.extend(node2csv(item, visibleColumns))
    return rows

def node2csv(item, visibleColumns, level=0):
    rows = [[' '*level + visibleColumns[0].render(item)] + \
            [column.render(item) for column in visibleColumns[1:]]]
    for child in item.children():
        rows.extend(node2csv(child, visibleColumns, level+1))
    return rows
