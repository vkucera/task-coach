import optparse, meta

class OptionParser(optparse.OptionParser, object):
    def __init__(self, *args, **kwargs):
        super(OptionParser, self).__init__(*args, **kwargs)
        self.__addOptionGroups()
        self.__addOptions()

    def __addOptionGroups(self):
        self.__getAndAddOptions('OptionGroup', self.add_option_group)
        
    def __addOptions(self):
        self.__getAndAddOptions('Option', self.add_option)
        
    def __methodsEndingWith(self, suffix):
        return [method for name, method in vars(self.__class__).items() if
                name.endswith(suffix)]

    def __getAndAddOptions(self, suffix, addOption):
        for getOption in self.__methodsEndingWith(suffix):
            addOption(getOption(self))

                
class OptionGroup(optparse.OptionGroup, object):
    pass
    
    
class ApplicationOptionParser(OptionParser):
    def __init__(self, *args, **kwargs):
        kwargs['usage'] = 'usage: %prog [options] [.tsk file]'
        kwargs['version'] = '%s %s'%(meta.data.name, meta.data.version)
        super(ApplicationOptionParser, self).__init__(*args, **kwargs)
        
    def profileOption(self):
        return optparse.Option('-p', '--profile', default=False, 
            action='store_true', help=optparse.SUPPRESS_HELP)

        