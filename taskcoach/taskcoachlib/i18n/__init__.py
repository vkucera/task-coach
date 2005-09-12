import patterns, wx

class Translator:
    __metaclass__ = patterns.Singleton
    
    def __init__(self, language=None):
        if language:
            if language not in ('en_US', 'en_GB'):
                module = __import__(language, globals())
                self.__language = module.dict
                self.__encoding = module.encoding                
            li = wx.Locale.FindLanguageInfo(language)
            self.__locale = wx.Locale(li.Language)
         
    def translate(self, string):
        try:
            return self.__language[string].decode(self.__encoding)
        except (AttributeError, KeyError):
            return string
        
def _(string):
    return Translator().translate(string)

