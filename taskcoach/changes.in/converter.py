import textwrap

class ChangeToTextConverter:
    def __init__(self):
        self._textWrapper = textwrap.TextWrapper(initial_indent='- ', 
                subsequent_indent='  ', width=78)

    def convert(self, change):
        result = change.description
        if change.sourceForgeIds:
            result += ' (%s)'%', '.join(change.sourceForgeIds)
        return self._textWrapper.fill(result)


class ReleaseToTextConverter:
    def __init__(self):
        self._changeToTextConverter = ChangeToTextConverter()

    def __addS(self, listToCount):
        return len(listToCount) > 1 and 's' or ''

    def convert(self, release):
        result = ['Release %s - %s'%(release.number, release.date)]
        for section, list in [('Bug%s fixed', release.bugsFixed),
                ('Feature%s added', release.featuresAdded),
                ('Feature%s removed', release.featuresRemoved)]:
            if list:
                result.append('\n%s:'%(section%self.__addS(list)))
                for change in list:
                    result.append(self._changeToTextConverter.convert(change))
        return '\n'.join(result)+'\n\n\n'



