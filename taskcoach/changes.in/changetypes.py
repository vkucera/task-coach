import textwrap

class Release:
    def __init__(self, number, date, bugsFixed=None, featuresAdded=None,
            featuresRemoved=None, featuresChanged=None, 
            dependenciesChanged=None, implementationChanged=None,
            websiteChanges=None, summary=''):
        self.number = number
        self.date = date
        self.summary = summary
        self.bugsFixed = bugsFixed or []
        self.featuresAdded = featuresAdded or []
        self.featuresRemoved = featuresRemoved or []
        self.featuresChanged = featuresChanged or []
        self.dependenciesChanged = dependenciesChanged or []
        self.implementationChanged = implementationChanged or []
        self.websiteChanges = websiteChanges or []


class Change(object):
    def __init__(self, description, *sourceForgeIds):
        self.description = description
        self.sourceForgeIds = sourceForgeIds


class Bug(Change):
    pass


class Feature(Change):
    pass


class Dependency(Change):
    pass


class Implementation(Change):
    pass


class Website(Change):
    def __init__(self, description, url, *sourceForgeIds):
        super(Website, self).__init__(description, *sourceForgeIds)
        self.url = url