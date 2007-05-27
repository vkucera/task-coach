import patterns, wx

class Translator:
    __metaclass__ = patterns.Singleton
    
    def __init__(self, languageAndCountry=None):
        if not languageAndCountry:
            return

        language = languageAndCountry[:2]

        # Import translation dicstionary
        if language != 'en': 
            module = __import__(language, globals())
            self.__language = module.dict
            self.__encoding = module.encoding

        # Try to find language info 
        for localeString in languageAndCountry, language:
            li = wx.Locale.FindLanguageInfo(localeString)
            if li:
                self.__locale = wx.Locale(li.Language)
                break

         
    def translate(self, string):
        try:
            return self.__language[string].decode(self.__encoding)
        except (AttributeError, KeyError):
            return string
        
def _(string):
    return Translator().translate(string)

