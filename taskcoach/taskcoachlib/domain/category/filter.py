import category, patterns
from domain import base

class CategoryFilter(base.Filter):
    def __init__(self, *args, **kwargs):
        self.__categories = kwargs.pop('categories')
        self.__filterOnlyWhenAllCategoriesMatch = \
            kwargs.pop('filterOnlyWhenAllCategoriesMatch', False)
        eventTypes = [self.__categories.addItemEventType(),
                      self.__categories.removeItemEventType(),
                      category.Category.categorizableAddedEventType(),
                      category.Category.categorizableRemovedEventType(),
                      category.Category.filterChangedEventType()]
        for eventType in eventTypes:
            patterns.Publisher().registerObserver(self.onCategoryChanged,
                                                  eventType=eventType)
        super(CategoryFilter, self).__init__(*args, **kwargs)
    
    def setFilterOnlyWhenAllCategoriesMatch(self, filterOnlyWhenAllCategoriesMatch=True):
        self.__filterOnlyWhenAllCategoriesMatch = filterOnlyWhenAllCategoriesMatch
        
    def filter(self, categorizables): # FIXME: generalize to categorizable
        filteredCategories = [category for category in self.__categories 
                              if category.isFiltered()]
        if filteredCategories:
            return [categorizable for categorizable in categorizables if \
                    self.filterCategorizable(categorizable, filteredCategories)]
        else:
            return categorizables
        
    def filterCategorizable(self, categorizable, filteredCategories):
        matches = [category.contains(categorizable, self.treeMode()) 
                   for category in filteredCategories]
        if self.__filterOnlyWhenAllCategoriesMatch:
            return False not in matches
        else:
            return True in matches
        
    def onCategoryChanged(self, event):
        self.reset()
