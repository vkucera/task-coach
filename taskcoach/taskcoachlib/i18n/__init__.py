'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

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

    
def currentLanguageIsRightToLeft():
    return wx.GetApp().GetLayoutDirection() == wx.Layout_RightToLeft       

def translate(string):
    return Translator().translate(string)

_ = translate # This prevents a warning from pygettext.py

