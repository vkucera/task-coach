import patterns

class Translator:
    __metaclass__ = patterns.Singleton
    
    def __init__(self, language=None):
        if language == 'nl':
            from nl import nl
            self.__language = nl
        
    def translate(self, string):
        try:
            return self.__language[string]
        except AttributeError, KeyError:
            return string
        
def _(string):
    return Translator().translate(string)

