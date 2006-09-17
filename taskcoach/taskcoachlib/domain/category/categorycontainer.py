import patterns


class CategoryContainer(patterns.ObservableSet):
    def rootItems(self):
        return [item for item in self if not item.parent()]
    
    def append(self, item):
        if item in self:
            return
        else:
            super(CategoryContainer, self).append(item)