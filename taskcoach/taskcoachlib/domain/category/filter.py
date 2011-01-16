'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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
    
    def filter(self, categorizables):
        filteredCategories = self.__categories.filteredCategories()
        if not filteredCategories:
            return categorizables
        
        filteredCategorizables = set()
        if self.__filterOnlyWhenAllCategoriesMatch:
            allowedCategorizables = set(categorizables)
            for category in filteredCategories:
                allowedCategorizables &= self.__categorizablesBelongingToCategory(category)
        else:
            allowedCategorizables = set()
            for category in filteredCategories: 
                allowedCategorizables |= self.__categorizablesBelongingToCategory(category)

        for categorizable in categorizables:
            categorizablesToInvestigate = set([categorizable]) 
            if self.treeMode():
                categorizablesToInvestigate.update(child for child in categorizable.children(recursive=True) \
                                                   if child in self.observable())
            if allowedCategorizables & categorizablesToInvestigate:
                filteredCategorizables.add(categorizable)
        return filteredCategorizables

    @staticmethod
    def __categorizablesBelongingToCategory(category):
        categorizables = category.categorizables(recursive=True)
        for categorizable in categorizables.copy():
            categorizables |= set(categorizable.children(recursive=True))            
        return categorizables
        
    def onFilterMatchingChanged(self, event):
        self.__filterOnlyWhenAllCategoriesMatch = eval(event.value())
        self.reset()

    def onCategoryChanged(self, event):
        self.reset()
