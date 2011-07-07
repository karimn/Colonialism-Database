import codecs, cStringIO, csv

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def _basewrite(self, row):
        self.writer.writerow(row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writeheader(self, model):
        self._basewrite([unicode(s.name).encode("utf-8") for s in model._meta.fields])

    def writerow(self, row):
        field_names = [s.name for s in row._meta.fields] 
        self._basewrite([unicode(getattr(row, n)).encode("utf-8") for n in field_names])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

