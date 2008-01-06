import patterns
from i18n import _

class CategoryList(patterns.CompositeList):
    newItemMenuText = _('New category...')
    newItemHelpText =  _('Insert a new category')
    editItemMenuText = _('Edit category...')
    editItemHelpText = _('Edit the selected categories')
    deleteItemMenuText = _('Delete category')
    deleteItemHelpText = _('Delete the selected categories')
    newSubItemMenuText = _('New subcategory...')
    newSubItemHelpText = _('Insert a new subcategory')
    
    def extend(self, categories):
        super(CategoryList, self).extend(categories)
        for category in self._compositesAndAllChildren(categories):
            for categorizable in category.categorizables():
                categorizable.addCategory(category)
                
    def removeItems(self, categories):
        super(CategoryList, self).removeItems(categories)
        for category in self._compositesAndAllChildren(categories):
            for categorizable in category.categorizables():
                categorizable.removeCategory(category)
        
        