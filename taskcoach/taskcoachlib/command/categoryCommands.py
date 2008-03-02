'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

import base
from i18n import _
from domain import category

class NewCategoryCommand(base.BaseCommand):
    def name(self):
        return _('New category')

    def __init__(self, *args, **kwargs):
        super(NewCategoryCommand, self).__init__(*args, **kwargs)
        self.items = self.createNewCategories()
        
    def createNewCategories(self):
        return [category.Category(subject=_('New category'))]
        
    def do_command(self):
        self.list.extend(self.items)

    def undo_command(self):
        self.list.removeItems(self.items)

    def redo_command(self):
        self.list.extend(self.items)


class NewSubCategoryCommand(NewCategoryCommand):
    def name(self):
        return _('New subcategory')
            
    def createNewCategories(self):
        return [parent.newChild(subject=_('New subcategory')) for parent in self.items]


class EditCategoryCommand(base.EditCommand):
    def name(self):
        return _('Edit category')
    
    def getItemsToSave(self):
        return self.items
    
    
class DragAndDropCategoryCommand(base.DragAndDropCommand):
    def name(self):
        return _('Drag and drop category')

