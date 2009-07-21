'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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

import wx, os, imp, tempfile
from taskcoachlib import patterns
import po2dict


class Translator:
    __metaclass__ = patterns.Singleton
    
    def __init__(self, language=None):
        if not language:
            return
        load = self._loadPoFile if language.endswith('.po') else self._loadModule
        module, localeStrings = load(language) 
        self._installModule(module)
        self._setLocale(*localeStrings)

    def _loadPoFile(self, poFilename):
        ''' Load the translation from a .po file by creating a python 
            module with po2dict and them importing that module. ''' 
        language = os.path.splitext(os.path.basename(poFilename))[0]
        pyFilename = self._tmpPyFilename()
        po2dict.make(poFilename, pyFilename)
        module = imp.load_source(language, pyFilename)
        os.remove(pyFilename)
        return module, (language,)
    
    def _tmpPyFilename(self):
        ''' Return a filename of a (closed) temporary .py file. '''
        tmpFile = tempfile.NamedTemporaryFile(suffix='.py')
        pyFilename = tmpFile.name
        tmpFile.close()
        return pyFilename

    def _loadModule(self, languageAndCountry):
        ''' Load the translation from a python module that has been 
            created from a .po file with po2dict before. '''
        language = languageAndCountry.split('_')[0] # e.g. 'nl_NL'.split('_')[0] == 'nl'
        for moduleName in languageAndCountry, language:
            try:
                module = __import__(moduleName, globals())
                break
            except ImportError:
                module = None
        return module, (languageAndCountry, language)

    def _installModule(self, module):
        ''' Make the module's translation dictionary and encoding available. '''
        if module:
            self.__language = module.dict
            self.__encoding = module.encoding

    def _setLocale(self, *localeStrings):
        ''' Try to set the locale, trying possibly multiple localeStrings. '''
        for localeString in localeStrings:
            languageInfo = wx.Locale.FindLanguageInfo(localeString)
            if languageInfo:
                self.__locale = wx.Locale(languageInfo.Language)
                break

    def translate(self, string):
        ''' Look up string in the current language dictionary. Return the
            passed string if no language dictionary is available or if the
            dictionary doesn't contain the string. '''
        try:
            return self.__language[string].decode(self.__encoding)
        except (AttributeError, KeyError):
            return string

    
def currentLanguageIsRightToLeft():
    return wx.GetApp().GetLayoutDirection() == wx.Layout_RightToLeft       

def translate(string):
    return Translator().translate(string)

_ = translate # This prevents a warning from pygettext.py

