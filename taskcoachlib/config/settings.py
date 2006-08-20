import ConfigParser, os, meta, defaults, patterns


class UnicodeAwareConfigParser(ConfigParser.SafeConfigParser):
    def set(self, section, setting, value):
        if type(value) == type(u''):
            value = value.encode('utf-8')
        ConfigParser.SafeConfigParser.set(self, section, setting, value)

    def get(self, section, setting):
        value = ConfigParser.SafeConfigParser.get(self, section, setting)
        return value.decode('utf-8')
    

class Settings(object, UnicodeAwareConfigParser):
    def __init__(self, load=True, *args, **kwargs):
        # Sigh, ConfigParser.SafeConfigParser is an old-style class, so we 
        # have to call the superclass __init__ explicitly:
        super(Settings, self).__init__(*args, **kwargs)
        UnicodeAwareConfigParser.__init__(self, *args, **kwargs) 
        self.setDefaults()
        self.__loadAndSave = load
        if load:
            self.read(self.filename()) # ConfigParser.read fails silently
        else:
            # Assume that if the settings are not to be loaded, we also 
            # should be quiet (i.e. we are probably in test mode):
            self.__beQuiet() 
        # FIXME: add some machinery to check whether values read in from
        # the TaskCoach.ini file are allowed values. We need some way to 
        # specify allowed values. That's easy for boolean and enumeration types,
        # but more difficult for e.g. color values and coordinates.
        
    def setDefaults(self):
        for section, settings in defaults.defaults.items():
            self.add_section(section)
            for key, value in settings.items():
                # Don't notify observers while we are initializing
                super(Settings, self).set(section, key, value)

    def __beQuiet(self):
        noisySettings = [('window', 'splash'), ('window', 'tips')]
        for section, setting in noisySettings:
            self.set(section, setting, 'False')
                
    def set(self, section, option, value):
        super(Settings, self).set(section, option, value)
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            '%s.%s'%(section, option), value))

    def getlist(self, section, option):
        return eval(self.get(section, option))
    
    def setlist(self, section, option, value):
        self.set(section, option, str(value))
        
    def save(self):
        if not self.__loadAndSave:
            return
        try:
            path = self.path()
            if not os.path.exists(path):
                os.mkdir(path)
            iniFile = file(self.filename(), 'w')
            self.write(iniFile)
            iniFile.close()
        except:
            raise # pass

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
