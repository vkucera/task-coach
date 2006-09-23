import generator, csv

class CSVWriter(object):
    def __init__(self, fd):
        self.__fd = fd

    def write(self, viewer):
        csvValues = generator.viewer2csv(viewer)
        csv.writer(self.__fd).writerows(csvValues)
