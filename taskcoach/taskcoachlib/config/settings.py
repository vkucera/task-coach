import ConfigParser, os, meta, defaults

class Settings(ConfigParser.SafeConfigParser, object):
    def __init__(self, load=True):
        super(Settings, self).__init__()
        self.setDefaults()
        if load:
            self.read(self.filename()) # ConfigParser.read fails silently

    def setDefaults(self):
        for section, settings in defaults.defaults.items():
            self.add_section(section)
            for key, value in settings.items():
                self.set(section, key, value)

    def save(self):
        try:
            path = self.path()
            if not os.path.exists(path):
                os.mkdir(path)
            fp = file(self.filename(), 'w')
            self.write(fp)
            fp.close()
        except:
            pass

    def path(self, environ=os.environ):
        try:
            path = os.path.join(environ['APPDATA'], meta.filename)
        except:
            path = os.path.expanduser("~")
            if path == "~":
                # path not expanded: there is no home dir (as on a Mac?)
                path = os.getcwd()
            path = os.path.join(path, '.%s'%meta.filename)
        return path

    def filename(self):
        return os.path.join(self.path(), '%s.ini'%meta.filename)

