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
    
    def do_command(self):
        self.toggle_category()
        
    undo_command = redo_command = do_command
        
    def toggle_category(self):
        event = patterns.Event()
        for item in self.items:
            if self.category in item.categories():
                self.category.removeCategorizable(item, event=event)
                item.removeCategory(self.category, event=event)
            else:
                self.category.addCategorizable(item, event=event)
                item.addCategory(self.category, event=event)
        event.send()  