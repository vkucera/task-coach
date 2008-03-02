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

import textwrap, changetypes, re


# Change (bugs fixed, features added, etc.) converters:

class ChangeConverter(object):
    def convert(self, change):
        result = self.preProcess(change.description)
        if hasattr(change, 'url'):
            result += ' (%s)'%self.convertURL(change.url)
        if change.sourceForgeIds:
            convertedIds = self.convertSourceForgeIds(change)
            result += ' (%s)'%', '.join(convertedIds)
        return self.postProcess(result)
    
    def preProcess(self, changeToBeConverted):
        return changeToBeConverted

    def postProcess(self, convertedChange):
        return convertedChange

    def convertSourceForgeIds(self, change):
        return [self.convertSourceForgeId(change, id) for id in change.sourceForgeIds]

    def convertSourceForgeId(self, change, sourceForgeId):
        return sourceForgeId

    def convertURL(self, url):
        return url
    

class ChangeToTextConverter(ChangeConverter):
    def __init__(self):
        self._textWrapper = textwrap.TextWrapper(initial_indent='- ', 
                subsequent_indent='  ', width=78)
        # Regular expression to remove multiple spaces, except when on
        # the start of a line:
        self._multipleSpaces = re.compile(r'(?<!^) +', re.M)

    def postProcess(self, convertedChange):
        convertedChange = self._textWrapper.fill(convertedChange)
        # Somehow the text wrapper introduces multiple spaces within
        # lines, this is a work around:
        convertedChange = self._multipleSpaces.sub(' ', convertedChange)
        return convertedChange

    def convertSourceForgeId(self, change, sourceForgeId):
        return 'SF#%s'%sourceForgeId
        

bugLink = '<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=%(id)s&group_id=130831&atid=719134">%(id)s</A>'

rfeLink = '<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=%(id)s&group_id=130831&atid=719137">%(id)s</A>'

noLink = '%(id)s'

class ChangeToHTMLConverter(ChangeConverter):

    def preProcess(self, changeToBeConverted):
        changeToBeConverted = re.sub('<', '&lt;', changeToBeConverted)
        changeToBeConverted = re.sub('>', '&gt;', changeToBeConverted)
        return changeToBeConverted
    
    def postProcess(self, convertedChange):
        listOfUrlAndTextFragments = re.split('(http://\S+)', convertedChange)
        listOfConvertedUrlsAndTextFragments = []
        for fragment in listOfUrlAndTextFragments:
            if fragment.startswith('http://'):
                fragment = self.convertURL(fragment)
            listOfConvertedUrlsAndTextFragments.append(fragment)
        convertedChange = ''.join(listOfConvertedUrlsAndTextFragments)
        return '<LI>%s</LI>'%convertedChange

    def convertSourceForgeId(self, change, sourceForgeId):
        if isinstance(change, changetypes.Bug):
            template = bugLink    
        elif isinstance(change, changetypes.Feature):
            template = rfeLink
        else:
            template = noLink
        return template%{'id': sourceForgeId}

    def convertURL(self, url):
        return '<A HREF="%s">%s</A>'%(url, url)


# Release converters:

class ReleaseConverter(object):
    def __init__(self):
        self._changeConverter = self.ChangeConverterClass()

    def _addS(self, listToCount):
        return {'s' : len(listToCount) > 1 and 's' or '',
                'y' : len(listToCount) > 1 and 'ies' or 'y' }

    def convert(self, release):
        result = [self.header(release), self.summary(release)]
        for section, list in [('Bug%(s)s fixed', release.bugsFixed),
                ('Feature%(s)s added', release.featuresAdded),
                ('Feature%(s)s changed', release.featuresChanged),
                ('Feature%(s)s removed', release.featuresRemoved),
                ('Implementation%(s)s changed', release.implementationChanged),
                ('Dependenc%(y)s changed', release.dependenciesChanged),
                ('Website change%(s)s', release.websiteChanges)]:
            if list:
                result.append(self.sectionHeader(section, list))
                for change in list:
                    result.append(self._changeConverter.convert(change))
                result.append(self.sectionFooter(section, list))
        result = [line for line in result if line]
        return '\n'.join(result)+'\n\n\n'

    def header(self, release):
        return 'Release %s - %s'%(release.number, release.date)

    def summary(self, release):
        return release.summary
    
    def sectionHeader(self, section, list):
        return '\n%s:'%(section%self._addS(list))
        
    def sectionFooter(self, section, list):
        return ''


class ReleaseToTextConverter(ReleaseConverter):
    ChangeConverterClass = ChangeToTextConverter


class ReleaseToHTMLConverter(ReleaseConverter):
    ChangeConverterClass = ChangeToHTMLConverter

    def header(self, release):
        return '<H4>%s</H4>'%super(ReleaseToHTMLConverter, self).header(release)

    def sectionHeader(self, section, list):
        return super(ReleaseToHTMLConverter, self).sectionHeader(section, 
            list) + '\n<UL>'

    def sectionFooter(self, section, list):
        return '</UL>'

    def summary(self, release):
        summaryText = super(ReleaseToHTMLConverter, self).summary(release)
        if summaryText:
            return '<P>%s</P>'%summaryText
        else:
            return ''
