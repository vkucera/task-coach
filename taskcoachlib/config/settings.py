import ConfigParser, os, sys, meta, defaults, patterns, wx


class UnicodeAwareConfigParser(ConfigParser.SafeConfigParser):
    def set(self, section, setting, value):
        if type(value) == type(u''):
            value = value.encode('utf-8')
        ConfigParser.SafeConfigParser.set(self, section, setting, value)

    def get(self, section, setting):
        value = ConfigParser.SafeConfigParser.get(self, section, setting)
        return value.decode('utf-8')
    

class Settings(patterns.Observable, patterns.Observer, UnicodeAwareConfigParser):
    def __init__(self, load=True, *args, **kwargs):
        # Sigh, ConfigParser.SafeConfigParser is an old-style class, so we 
        # have to call the superclass __init__ explicitly:
        super(Settings, self).__init__(*args, **kwargs)
        UnicodeAwareConfigParser.__init__(self, *args, **kwargs) 
        self.setDefaults()
        self.__loadAndSave = load
        if load:
            # First, try to load the settings file from the program directory,
            # if that fails, load the settings file from the settings directory
            if not self.read(self.filename(forceProgramDir=True)):
                self.read(self.filename()) 
        else:
            # Assume that if the settings are not to be loaded, we also 
            # should be quiet (i.e. we are probably in test mode):
            self.__beQuiet()
        self.registerObserver(self.onSettingsFileLocationChanged, 
                              'file.saveinifileinprogramdir') 
        # FIXME: add some machinery to check whether values read in from
        # the TaskCoach.ini file are allowed values. We need some way to 
        # specify allowed values. That's easy for boolean and enumeration types,
        # but more difficult for e.g. color values and coordinates.
        
    def onSettingsFileLocationChanged(self, event):
        saveIniFileInProgramDir = event.value() == 'True'
        if not saveIniFileInProgramDir:
            try:
                os.remove(self.filename(forceProgramDir=True))
            except:
                return
            
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
        self.notifyObservers(patterns.Event(self, '%s.%s'%(section, option), 
                             value))
            
    def setboolean(self, section, option, value):
        self.set(section, option, str(value))

    def getlist(self, section, option):
        return eval(self.get(section, option))
    
    def setlist(self, section, option, value):
        self.set(section, option, str(value))
        
    def save(self, showerror=wx.MessageBox):
        if not self.__loadAndSave:
            return
        try:
            path = self.path()
            if not os.path.exists(path):
                os.mkdir(path)
            iniFile = file(self.filename(), 'w')
            self.write(iniFile)
            iniFile.close()
        except Exception, message:
            showerror(_('Error while saving %s.ini:\n%s\n')% \
                      (meta.filename, message), caption=_('Save error'), 
                      style=wx.ICON_ERROR)

    def filename(self, forceProgramDir=False):
        return os.path.join(self.path(forceProgramDir), '%s.ini'%meta.filename)
    
    def path(self, forceProgramDir=False, environ=os.environ):
        if forceProgramDir or self.getboolean('file', 
                                              'saveinifileinprogramdir'):
            return self.pathToProgramDir()
        else:
            return self.pathToConfigDir(environ)

    def pathToProgramDir(self):
        path = sys.argv[0]
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        return path
    
    def pathToConfigDir(self, environ):
        try:
            path = os.path.join(environ['APPDATA'], meta.filename)
        except:
            path = os.path.expanduser("~")
            if path == "~":
                # path not expanded: apparently, there is no home dir
                path = os.getcwd()
            path = os.path.join(path, '.%s'%meta.filename)
        return path

