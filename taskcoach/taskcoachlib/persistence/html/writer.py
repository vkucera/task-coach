import generator

class HTMLWriter(object):
    def __init__(self, fd):
        self.__fd = fd

    def write(self, viewer):
        htmlText = generator.viewer2html(viewer)
        self.__fd.write(htmlText)
