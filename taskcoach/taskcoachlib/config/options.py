import optparse, meta

class OptionParser(optparse.OptionParser, object):
    def __init__(self, *args, **kwargs):
        self.super = super(OptionParser, self)
        self.super.__init__(*args, **kwargs)
        self.addOptionGroups()
        self.addOptions()

    def addOptionGroups(self):
        for optionGroup in self.optionGroups():
            self.add_option_group(optionGroup(self))

    def optionGroups(self):
        return [method for name, method in vars(self.__class__).items() if
                name.endswith('Options')]

    def addOptions(self):
        for option in self.options():
            self.add_option(option(self))
            
    def options(self):
        return [method for name, method in vars(self.__class__).items() if
                name.endswith('Option')]
 
                
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

        