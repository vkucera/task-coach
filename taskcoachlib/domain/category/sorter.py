import patterns
import category

class CategorySorter(patterns.ListDecorator):    
    def __init__(self, *args, **kwargs):
        super(CategorySorter, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.reset, 
            category.Category.subjectChangedEventType())
        
    def sortEventType(self):
        return '%s(%s).sorted'%(self.__class__, id(self))
    
    def extendSelf(self, categories):
        super(CategorySorter, self).extendSelf(categories)
        self.reset()

    # We don't override removeItemsFromSelf because there is no need to 
    # call self.reset() when items are removed since after removing items
    # the remaining items are still in the right order.

    def reset(self, event=None):
        oldSelf = self[:]
        self.sort(key=lambda category: category.subject(), reverse=False)
        if self != oldSelf:
            patterns.Publisher().notifyObservers(patterns.Event(self, 
                self.sortEventType()))


