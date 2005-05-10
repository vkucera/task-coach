import patterns, wx

class Translator:
    __metaclass__ = patterns.Singleton
    
    def __init__(self, language=None):
        if language and language.startswith('nl'):
            import nl
            self.__language = nl.dict
            self.__encoding = nl.encoding
        elif language and language.startswith('fr'):
            import fr
            self.__language = fr.dict
            self.__encoding = fr.encoding
        if language:
            li = wx.Locale.FindLanguageInfo(language)
            self.__locale = wx.Locale(li.Language)
        
    def translate(self, string):
        try:
            return self.__language[string].decode(self.__encoding)
        except (AttributeError, KeyError):
            return string
        
def _(string):
    return Translator().translate(string)

