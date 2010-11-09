'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

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
from category import Category


class CategoryFilter(base.Filter):
    def __init__(self, *args, **kwargs):
        self.__categories = kwargs.pop('categories')
        self.__filterOnlyWhenAllCategoriesMatch = \
            kwargs.pop('filterOnlyWhenAllCategoriesMatch', False)
        for eventType in (self.__categories.addItemEventType(),
                          self.__categories.removeItemEventType()):
            patterns.Publisher().registerObserver(self.onCategoryChanged,
                                                  eventType=eventType, 
                                                  eventSource=self.__categories)
        eventTypes = (Category.categorizableAddedEventType(),
                      Category.categorizableRemovedEventType(),
                      Category.filterChangedEventType())
        for eventType in eventTypes:
            patterns.Publisher().registerObserver(self.onCategoryChanged,
                                                  eventType=eventType)
        patterns.Publisher().registerObserver(self.onFilterMatchingChanged,
            eventType='view.categoryfiltermatchall')

        super(CategoryFilter, self).__init__(*args, **kwargs)
    
    def setFilterOnlyWhenAllCategoriesMatch(self, filterOnlyWhenAllCategoriesMatch=True):
        self.__filterOnlyWhenAllCategoriesMatch = filterOnlyWhenAllCategoriesMatch
        
    def filter(self, categorizables):
        filteredCategories = self.__categories.filteredCategories()
        if filteredCategories:
            return self.filteredCategorizables(categorizables, filteredCategories)
        else:
            return categorizables
        
    def filteredCategorizables(self, categorizables, filteredCategories):
        return [categorizable for categorizable in categorizables if \
                self.categorizableIsFiltered(categorizable, filteredCategories)]
        
    def categorizableIsFiltered(self, categorizable, filteredCategories):
        matches = self.categoriesContain(filteredCategories, categorizable) 
        if self.__filterOnlyWhenAllCategoriesMatch:
            return False not in matches
        else:
            return True in matches
        
    def categoriesContain(self, categories, categorizable):
        ''' Return whether the categorizable belongs to the categories. If an
            ancestor of the categorizable belong to a category, the 
            categorizable itself belongs to the category too. '''
        matches = []
        categorizablesToInvestigate = set([categorizable] + categorizable.ancestors())
        if self.treeMode():
            categorizablesToInvestigate.update(child for child in categorizable.children(recursive=True) \
                                               if child in self.observable() and \
                                               self.categorizableIsFiltered(child, categories))

        for category in categories:
            containedCategorizables = category.categorizables(recursive=True)
            matches.append(bool(containedCategorizables & categorizablesToInvestigate))
            
        return matches
            
    def onFilterMatchingChanged(self, event):
        self.__filterOnlyWhenAllCategoriesMatch = eval(event.value())
        self.reset()

    def onCategoryChanged(self, event):
        self.reset()
