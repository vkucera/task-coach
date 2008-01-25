import patterns
from domain import base


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
        
    def categories(self, recursive=False):
        result = set(self._categories)
        if recursive and self.parent() is not None:
            result |= self.parent().categories(recursive=True)
        return result
    
    @classmethod
    def categoryAddedEventType(class_):
        return 'categorizable.category.add'

    def addCategory(self, category):
        if category not in self._categories:
            self._categories.add(category)
            self.notifyObservers(patterns.Event(self, 
                self.categoryAddedEventType(), category))
            self.notifyChildObserversOfCategoryChange(category, 'add')
            if category.color():
                self.notifyObserversOfCategoryColorChange()
                
    @classmethod
    def categoryRemovedEventType(class_):
        return 'categorizable.category.remove'
    
    def removeCategory(self, category):
        if category in self._categories:
            self._categories.discard(category)
            self.notifyObservers(patterns.Event(self, 
                self.categoryRemovedEventType(), category))
            self.notifyChildObserversOfCategoryChange(category, 'remove')
            if category.color():
                self.notifyObserversOfCategoryColorChange()
                
    def setCategories(self, categories):
        oldCategories = set(self._categories)
        for category in oldCategories:
            if category not in categories:
                self.removeCategory(category)
        for category in categories:
            self.addCategory(category)
        
    def categoryColor(self):
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
        elif self.parent():
            return self.parent().categoryColor()
        else:
            return None

    @classmethod
    def totalCategoryAddedEventType(class_):
        return 'categorizable.totalCategory.add'

    @classmethod
    def totalCategoryRemovedEventType(class_):
        return 'categorizable.totalCategory.remove'
            
    def notifyChildObserversOfCategoryChange(self, category, change):
        assert change in ('add', 'remove')
        if change == 'add':
            eventType = self.totalCategoryAddedEventType()
        else:
            eventType = self.totalCategoryRemovedEventType()
        for child in self.children(recursive=True):
            self.notifyObservers(patterns.Event(child, eventType, category))
   
    @classmethod
    def categorySubjectChangedEventType(class_):
        return 'categorizable.category.subject'
             
    def notifyObserversOfCategorySubjectChange(self, category):
        self.notifyObservers(patterns.Event(self, 
            self.categorySubjectChangedEventType(), category.subject()))
        self.notifyObserversOfTotalCategorySubjectChange(category)
    
    @classmethod
    def totalCategorySubjectChangedEventType(class_):
        return 'categorizable.totalCategory.subject'
    
    def notifyObserversOfTotalCategorySubjectChange(self, category):
        for categorizable in [self] + self.children(recursive=True):
            self.notifyObservers(patterns.Event(categorizable, 
                self.totalCategorySubjectChangedEventType(), 
                category.subject()))
            
    @classmethod
    def categoryColorChangedEventType(class_):
        return 'categorizable.category.color'
            
    def notifyObserversOfCategoryColorChange(self):
        for categorizable in [self] + self.children(recursive=True):
            self.notifyObservers(patterns.Event(categorizable,
                self.categoryColorChangedEventType(), 
                categorizable.categoryColor()))

            
class Category(base.CompositeObject):
    def __init__(self, subject, categorizables=None, children=None, filtered=False, 
                 parent=None, description='', color=None, *args, **kwargs):
        super(Category, self).__init__(subject=subject, children=children or [], 
                                       parent=parent, description=description,
                                       *args, **kwargs)
        self.__categorizables = categorizables or []
        self.__filtered = filtered
        self.__color = color
            
    @classmethod
    def filterChangedEventType(class_):
        return 'category.filter'
    
    @classmethod
    def categorizableAddedEventType(class_):
        return 'category.categorizable.added'
    
    @classmethod
    def categorizableRemovedEventType(class_):
        return 'category.categorizable.removed'
    
    @classmethod
    def colorChangedEventType(class_):
        return 'category.color'
            
    def __getstate__(self):
        state = super(Category, self).__getstate__()
        state.update(dict(categorizables=self.__categorizables[:], 
                          filtered=self.__filtered, color=self.__color))
        return state
        
    def __setstate__(self, state):
        super(Category, self).__setstate__(state)
        self.__categorizables = state['categorizables']
        self.__filtered = state['filtered']
        self.__color = state['color']
        
    def copy(self):
        return self.__class__(self.subject(), self.categorizables(), 
                              [child.copy() for child in self.children()],
                              self.isFiltered(), self.parent(), 
                              self.description(), self.color())
        
    def setSubject(self, *args, **kwargs):
        if super(Category, self).setSubject(*args, **kwargs):
            for categorizable in self.categorizables(recursive=True):
                categorizable.notifyObserversOfCategorySubjectChange(self)
    
    def categorizables(self, recursive=False):
        result = []
        if recursive:
            for child in self.children():
                result.extend(child.categorizables(recursive))
        result.extend(self.__categorizables)
        return result
    
    def addCategorizable(self, categorizable):
        if categorizable not in self.__categorizables: # FIXME: use set
            self.__categorizables.append(categorizable)
            self.notifyObservers(patterns.Event(self, 
                self.categorizableAddedEventType(), categorizable))
            
    def removeCategorizable(self, categorizable):
        if categorizable in self.__categorizables:
            self.__categorizables.remove(categorizable)
            self.notifyObservers(patterns.Event(self, 
                self.categorizableRemovedEventType(), categorizable))
            
    def isFiltered(self):
        return self.__filtered
    
    def setFiltered(self, filtered=True):
        if filtered != self.__filtered:
            self.__filtered = filtered
            self.notifyObservers(patterns.Event(self, 
                self.filterChangedEventType(), filtered))
        if filtered:
            self._turnOffFilteringOfParent()
            self._turnOffFilteringOfChildren()
            
    def _turnOffFilteringOfChildren(self):
        for child in self.children():
            child.setFiltered(False)
            child._turnOffFilteringOfChildren()
            
    def _turnOffFilteringOfParent(self):
        parent = self.parent()
        if parent:
            parent.setFiltered(False)
            parent._turnOffFilteringOfParent()
        
    def contains(self, categorizable, treeMode=False):
        containedCategorizables = self.categorizables(recursive=True)
        if treeMode:
            categorizablesToInvestigate = categorizable.family()
        else:
            categorizablesToInvestigate = [categorizable] + categorizable.ancestors()
        for categorizableToInvestigate in categorizablesToInvestigate:
            if categorizableToInvestigate in containedCategorizables:
                return True
        return False
    
    def color(self, recursive=True):
        if self.__color is None and recursive and self.parent():
            return self.parent().color()
        else:
            return self.__color
    
    def setColor(self, color):
        if color != self.__color:
            self.__color = color
            self.notifyObserversOfColorChange(color)
            for categorizable in self.categorizables(recursive=True):
                categorizable.notifyObserversOfCategoryColorChange()
            
    def notifyObserversOfColorChange(self, color):
        self.notifyObservers(patterns.Event(self, 
            self.colorChangedEventType(), color))
        for child in self.children():
            child.notifyObserversOfParentColorChange(color)
                
    def notifyObserversOfParentColorChange(self, color):
        ''' If this category has its own color, do nothing. If this category
            uses the color of its parent, notify its observers of the color 
            change. And similarly for the children of this category. '''
        if self.__color is None:
            self.notifyObservers(patterns.Event(self, 
                                 self.colorChangedEventType(), color))
            for child in self.children():
                child.notifyObserversOfParentColorChange(color)
        