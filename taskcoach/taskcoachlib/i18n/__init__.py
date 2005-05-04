import patterns, wx

class Translator:
    __metaclass__ = patterns.Singleton
    
    def __init__(self, language=None):
        if language == 'nl':
            import nl
            self.__language = nl.dict
            self.__encoding = nl.encoding
            #self.__locale = wx.Locale(wx.LANGUAGE_DUTCH) # dutch calendarctrl not working properly
        elif language == 'fr':
            import fr
            self.__language = fr.dict
            self.__encoding = fr.encoding
            self.__locale = wx.Locale(wx.LANGUAGE_FRENCH)
        
    def translate(self, string):
        try:
            return self.__language[string].decode(self.__encoding)
        except (AttributeError, KeyError):
            return string
        
def _(string):
    return Translator().translate(string)

