import patterns, wx

class Translator:
    __metaclass__ = patterns.Singleton
    
    def __init__(self, language=None):
        if language and language.startswith('nl'):
            import nl_NL
            self.__language = nl_NL.dict
            self.__encoding = nl_NL.encoding
        elif language and language.startswith('fr'):
            import fr_FR
            self.__language = fr_FR.dict
            self.__encoding = fr_FR.encoding
        elif language and language.startswith('zh'):
            import zh_CN
            self.__language = zh_CN.dict
            self.__encoding = zh_CN.encoding
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

