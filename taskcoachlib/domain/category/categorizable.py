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

from taskcoachlib import patterns
from taskcoachlib.domain import base


class CategorizableCompositeObject(base.CompositeObject):
    ''' CategorizableCompositeObjects are composite objects that can be
        categorized by adding them to one or more categories. Examples of
        categorizable composite objects are tasks and notes. '''
        
    def __init__(self, *args, **kwargs):
        self._categories = set(kwargs.pop('categories', None) or [])
        super(CategorizableCompositeObject, self).__init__(*args, **kwargs)
        
    def __getstate__(self):
        state = super(CategorizableCompositeObject, self).__getstate__()
        state.update(dict(categories=self.categories()))
        return state

    def __setstate(self, state):
        super(CategorizableCompositeObject, self).__setstate__(state)
        self.setCategories(state['categories'])

    def __getcopystate__(self):
        state = super(CategorizableCompositeObject, self).__getcopystate__()
        state.update(dict(categories=self.categories()))
        return state
        
    def categories(self, recursive=False):
        result = set(self._categories)
        if recursive and self.parent() is not None:
            result |= self.parent().categories(recursive=True)
        return result
    
    @classmethod
    def categoryAddedEventType(class_):
        return 'categorizable.category.add'

    def addCategory(self, category):
        if category in self._categories:
            return
        self._categories.add(category)
        event = patterns.Event(self.categoryAddedEventType(), self, category)
        for child in self.children(recursive=True):
            event.addSource(child, category, type=child.totalCategoryAddedEventType())
        if category.color():
            event = self.colorChangedEvent(event, category.color())
        event.send()

    @classmethod
    def categoryRemovedEventType(class_):
        return 'categorizable.category.remove'
    
    def removeCategory(self, category):
        if category not in self._categories:
            return
        self._categories.discard(category)
        event = patterns.Event(self.categoryRemovedEventType(), self, category)
        for child in self.children(recursive=True):
            event.addSource(child, category, type=child.totalCategoryRemovedEventType())
        if category.color():
            event = self.colorChangedEvent(event, category.color())
        event.send()
        
    def setCategories(self, categories):
        oldCategories = set(self._categories)
        for category in oldCategories:
            if category not in categories:
                self.removeCategory(category)
        for category in categories:
            self.addCategory(category)

    def color(self, recursive=True):
        myOwnColor = super(CategorizableCompositeObject, self).color(False)
        if myOwnColor or not recursive:
            return myOwnColor
        categoryBasedColor = self._categoryColor()
        if categoryBasedColor:
            return categoryBasedColor
        if recursive:
            return super(CategorizableCompositeObject, self).color(True)
        else:
            return None
        
    def _categoryColor(self):
        ''' If a categorizable object belongs to a category that has a color 
            associated with it, the categorizable object is colored accordingly. 
            When a categorizable object belongs to multiple categories, the 
            color is mixed. If a categorizable composite object has no color of 
            its own, it uses its parent's color. '''
        colorSum, colorCount = [0, 0, 0, 0], 0
        for category in self.categories():
            categoryColor = category.color()
            if categoryColor:
                try:
                    categoryColor = categoryColor.Get(includeAlpha=True)
                except AttributeError:
                    pass # categoryColor is already a tuple
                for colorIndex in range(4): 
                    colorSum[colorIndex] += categoryColor[colorIndex]
                colorCount += 1
        if colorCount:
            return (colorSum[0]/colorCount, colorSum[1]/colorCount,
                    colorSum[2]/colorCount, colorSum[3]/colorCount)
        else:
            return None
            
    @classmethod
    def totalCategoryAddedEventType(class_):
        return 'categorizable.totalCategory.add'

    @classmethod
    def totalCategoryRemovedEventType(class_):
        return 'categorizable.totalCategory.remove'
            
    @classmethod
    def categorySubjectChangedEventType(class_):
        return 'categorizable.category.subject'
    
    @classmethod
    def totalCategorySubjectChangedEventType(class_):
        return 'categorizable.totalCategory.subject'
            
    @classmethod
    def modificationEventTypes(class_):
        eventTypes = super(CategorizableCompositeObject, class_).modificationEventTypes()
        return eventTypes + [class_.categoryAddedEventType(),
                             class_.categoryRemovedEventType()]
