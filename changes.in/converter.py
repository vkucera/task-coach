import textwrap, domain


# Change (bugs fixed, features added, etc.) converters:

class ChangeConverter(object):
    def convert(self, change):
        result = change.description
        if change.sourceForgeIds:
            convertedIds = self.convertSourceForgeIds(change)
            result += ' (%s)'%', '.join(convertedIds)
        return self.postProcess(result)

    def postProcess(self, convertedChange):
        return convertedChange

    def convertSourceForgeIds(self, change):
        return [self.convertSourceForgeId(change, id) for id in change.sourceForgeIds]

    def convertSourceForgeId(self, change, sourceForgeId):
        return sourceForgeId


class ChangeToTextConverter(ChangeConverter):
    def __init__(self):
        self._textWrapper = textwrap.TextWrapper(initial_indent='- ', 
                subsequent_indent='  ', width=78)

    def postProcess(self, convertedChange):
        return self._textWrapper.fill(convertedChange)

    def convertSourceForgeId(self, change, sourceForgeId):
        return 'SF#%s'%sourceForgeId
        

bugLink = '<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=%(id)s&group_id=130831&atid=719134">%(id)s</A>'

rfeLink = '<A HREF="https://sourceforge.net/tracker/index.php?func=detail&aid=%(id)s&group_id=130831&atid=719137">%(id)s</A>'

noLink = '%(id)s'

class ChangeToHTMLConverter(ChangeConverter):

    def postProcess(self, convertedChange):
        return '<LI>%s</LI>'%convertedChange

    def convertSourceForgeId(self, change, sourceForgeId):
        if isinstance(change, domain.Bug):
            template = bugLink    
        elif isinstance(change, domain.Feature):
            template = rfeLink
        else:
            template = noLink
        return template%{'id': sourceForgeId}


# Release converters:

class ReleaseConverter(object):
    def __init__(self):
        self._changeConverter = self.ChangeConverterClass()

    def _addS(self, listToCount):
        return len(listToCount) > 1 and 's' or ''

    def convert(self, release):
        result = [self.header(release)]
        for section, list in [('Bug%s fixed', release.bugsFixed),
                ('Feature%s added', release.featuresAdded),
                ('Feature%s removed', release.featuresRemoved)]:
            if list:
                result.append(self.sectionHeader(section, list))
                for change in list:
                    result.append(self._changeConverter.convert(change))
                result.append(self.sectionFooter(section, list))
        result = [line for line in result if line]
        return '\n'.join(result)+'\n\n\n'

    def header(self, release):
        return 'Release %s - %s'%(release.number, release.date)

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
