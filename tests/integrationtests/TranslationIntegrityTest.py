import test, i18n, meta, string


class TranslationIntegrityTests(object):
    ''' Unittests for translations. This class is subclassed below for each
        translated string in each language. '''
        
    def testMatchingNonLiterals(self):
        for symbol in '\t', '|', '%s', '%d', '%.2f', '%(name)s', '%(version)s':
            self.assertEqual(self.englishString.count(symbol), 
                self.translatedString.count(symbol),
                "Symbol ('%s') doesn't match for '%s' and '%s'"%(symbol,
                    self.englishString, self.translatedString))
            
    def testMatchingAccelerators(self):
        # Translated strings should have the same number of accelerators (&)
        # as the original, which in turn should be zero or one. However, 
        # because we're just starting testing for this, the current version
        # of this test is a bit less strict and we only make sure both the 
        # original as the translated string have zero or one accelerators. '''
        for string in self.englishString, self.translatedString:
            self.failUnless(string.count('&') in [0,1], 
                "'%s' has more than one '&'"%string)
            
    def testMatchingShortCut(self):
        for shortcutPrefix in ('Ctrl+', 'Shift+', 'Alt+',
                               'Shift+Ctrl+', 'Shift+Alt+'):
            self.assertEqual(self.englishString.count(shortcutPrefix),
                             self.translatedString.count(shortcutPrefix),
                             "Shortcut prefix ('%s') doesn't match for '%s' and '%s'"%(shortcutPrefix,
                                 self.englishString, self.translatedString))

    def testMatchingEllipses(self):
        ellipsis = '...'
        self.assertEqual(self.englishString.count(ellipsis),
                         self.translatedString.count(ellipsis),
                         "Ellipses ('...') don't match for '%s' and '%s'"%(self.englishString, self.translatedString))


def getLanguages():
    return [language for language in meta.data.languages.values() \
            if language is not None]
        

def createTestCaseClassName(language, englishString, 
                              prefix='TranslationIntegrityTest'):
    ''' Generate a class name for the test case class based on the language
        and the English string. '''
    # Make sure we only use characters allowed in Python identifiers:
    englishString = englishString.replace(' ', '_')
    allowableCharacters = string.ascii_letters + string.digits + '_'
    englishString = ''.join([char for char in englishString \
                             if char in allowableCharacters])
    className = '%s_%s_%s'%(prefix, language, englishString)
    count = 0
    while className in globals(): # Make sure className is unique
        count += 1
        className = '%s_%s_%s_%d'%(prefix, language, englishString, count)
    return className


def createTestCaseClass(className, language, englishString, translatedString):
    class_ = type(className, (TranslationIntegrityTests, test.TestCase), {})
    class_.language = language
    class_.englishString = englishString
    class_.translatedString = translatedString
    return class_


for language in getLanguages():
    translation = __import__('i18n.%s'%language, fromlist=['dict'])
    for englishString, translatedString in translation.dict.iteritems():        
        className = createTestCaseClassName(language, englishString)
        class_ = createTestCaseClass(className, language, englishString,
                                     translatedString)
        globals()[className] = class_