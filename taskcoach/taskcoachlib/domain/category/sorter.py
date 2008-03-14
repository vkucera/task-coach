from domain import base
import category


class CategorySorter(base.TreeSorter):
    DomainObjectClass = category.Category
    EventTypePrefix = 'category'

