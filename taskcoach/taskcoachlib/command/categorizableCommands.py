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

from taskcoachlib.i18n import _
from taskcoachlib import patterns
import base


class ToggleCategoryCommand(base.BaseCommand):
    def name(self):
        return _('Toggle category')
    
    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category')
        super(ToggleCategoryCommand, self).__init__(*args, **kwargs) 
        # Keep track of previous category per categorizable in case of mutual 
        # exclusive categories:
        self.__previous_category = dict()
        
    def do_command(self):
        self.toggle_category()
        
    undo_command = redo_command = do_command
        
    def toggle_category(self):
        event = patterns.Event()
        for item in self.items:
            if self.category in item.categories():
                self.category.removeCategorizable(item, event=event)
                item.removeCategory(self.category, event=event)
                if self.category.isMutualExclusive():
                    self.restore_previous_category(item, event)
            else:
                self.category.addCategorizable(item, event=event)
                item.addCategory(self.category, event=event)
                if self.category.isMutualExclusive():
                    self.remove_previous_category(item, event)
        event.send()
        
    def remove_previous_category(self, item, event):
        for sibling in self.category.siblings():
            if item in sibling.categorizables():
                sibling.removeCategorizable(item, event=event)
                item.removeCategory(sibling, event=event)
                self.__previous_category[item] = sibling
                break

    def restore_previous_category(self, item, event):
        if item in self.__previous_category:
            previous_category = self.__previous_category[item]
            previous_category.addCategorizable(item, event=event)
            item.addCategory(previous_category, event=event)
