import generator

class HTMLWriter(object):
    def __init__(self, fd):
        self.__fd = fd

    def write(self, viewer, selectionOnly=False):
        htmlText = generator.viewer2html(viewer, selectionOnly)
        self.__fd.write(htmlText)
