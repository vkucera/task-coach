import generator, csv, cStringIO


class UnicodeCSVWriter:
    ''' A CSV writer that writes rows to a CSV file encoded in utf-8. 
        Based on http://docs.python.org/lib/csv-examples.html
    '''
    def __init__(self, fd, *args, **kwargs):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, *args, **kwargs)
        self.fd = fd

    def writerow(self, row):
        self.writer.writerow([cell.encode('utf-8') for cell in row])
        # Fetch UTF-8 output from the queue 
        data = self.queue.getvalue()
        data = data.decode('utf-8')
        self.fd.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class CSVWriter(object):
    def __init__(self, fd):
        self.__fd = fd

    def write(self, viewer):
        csvRows = generator.viewer2csv(viewer)
        UnicodeCSVWriter(self.__fd).writerows(csvRows)