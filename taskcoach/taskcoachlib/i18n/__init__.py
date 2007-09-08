import patterns, wx

class Translator:
    __metaclass__ = patterns.Singleton
    
    def __init__(self, languageAndCountry=None):
        if languageAndCountry:
            language = languageAndCountry[:2] # e.g. 'nl_NL'[:2] == 'nl'
            self._importTranslation(languageAndCountry, language)
            self._setLocale(languageAndCountry, language)

    def _importTranslation(self, languageAndCountry, language):
        if language != 'en':
            try: 
                module = __import__(languageAndCountry, globals())
            except ImportError:
                module = __import__(language, globals())
            self.__language = module.dict
            self.__encoding = module.encoding

    def _setLocale(self, *localeStrings):
        for localeString in localeStrings:
            languageInfo = wx.Locale.FindLanguageInfo(localeString)
            if languageInfo:
                self.__locale = wx.Locale(languageInfo.Language)
                break

    def translate(self, string):
        try:
            return self.__language[string].decode(self.__encoding)
        except (AttributeError, KeyError):
            return string
        
def translate(string):
    return Translator().translate(string)

_ = translate # This prevents a warning from pygettext.py
