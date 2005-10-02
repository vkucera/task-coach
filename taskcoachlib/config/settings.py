import ConfigParser, os, meta, defaults, patterns

class Settings(patterns.Observable, ConfigParser.SafeConfigParser):
    def __init__(self, load=True, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        ConfigParser.SafeConfigParser.__init__(self, *args, **kwargs) # sigh, SafeConfigParser is not cooperative
        self.setDefaults()
        self.__loadAndSave = load
        if load:
            self.read(self.filename()) # ConfigParser.read fails silently

    def setDefaults(self):
        for section, settings in defaults.defaults.items():
            self.add_section(section)
            for key, value in settings.items():
                self.set(section, key, value)
                
    def set(self, section, option, value):
        super(Settings, self).set(section, option, value)
        self.notifyObservers(patterns.Notification(self, section=section, option=option, value=value), (section, option))

    def save(self):
        if not self.__loadAndSave:
            return
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
