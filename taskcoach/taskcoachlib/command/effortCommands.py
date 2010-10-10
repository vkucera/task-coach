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
from taskcoachlib.i18n import _
from taskcoachlib.domain import effort
import base


class NewEffortCommand(base.BaseCommand):
    plural_name = _('New efforts')
    singular_name = _('New effort of "%s"')
    
    def __init__(self, *args, **kwargs):
        super(NewEffortCommand, self).__init__(*args, **kwargs)
        self.items = self.efforts = [effort.Effort(task) for task in self.items]

    def name_subject(self, effort):
        return effort.task().subject()
        
    def do_command(self):
        for effort in self.efforts: # pylint: disable-msg=W0621
            effort.task().addEffort(effort)
            
    def undo_command(self):
        for effort in self.efforts: # pylint: disable-msg=W0621
            effort.task().removeEffort(effort)
            
    redo_command = do_command
    

class DeleteEffortCommand(base.DeleteCommand):
    plural_name = _('Delete efforts')
    singular_name = _('Delete effort "%s"')
    
    
class ChangeTaskCommand(base.BaseCommand):
    plural_name = _('Change task of effort')
    singular_name = _('Change task of "%s" effort')
    
    def __init__(self, *args, **kwargs):
        self.__task = kwargs.pop('task')
        super(ChangeTaskCommand, self).__init__(*args, **kwargs)
        self.__oldTasks = [item.task() for item in self.items]
        
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setTask(self.__task, event=event)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldTask in zip(self.items, self.__oldTasks):
            item.setTask(oldTask, event=event)

    def redo_command(self):
        self.do_command()


class ChangeEffortStartDateTimeCommand(base.BaseCommand):
    plural_name = _('Change effort start date and time')
    singular_name = _('Change effort start date and time of "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__datetime = kwargs.pop('datetime')
        super(ChangeEffortStartDateTimeCommand, self).__init__(*args, **kwargs)
        self.__oldDateTimes = [item.getStart() for item in self.items]
        
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setStart(self.__datetime, event=event)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldDateTime in zip(self.items, self.__oldDateTimes):
            item.setStart(oldDateTime, event=event)

    def redo_command(self):
        self.do_command()


class ChangeEffortStopDateTimeCommand(base.BaseCommand):
    plural_name = _('Change effort stop date and time')
    singular_name = _('Change effort stop date and time of "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__datetime = kwargs.pop('datetime')
        super(ChangeEffortStopDateTimeCommand, self).__init__(*args, **kwargs)
        self.__oldDateTimes = [item.getStop() for item in self.items]
        
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setStop(self.__datetime, event=event)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldDateTime in zip(self.items, self.__oldDateTimes):
            item.setStop(oldDateTime, event=event)

    def redo_command(self):
        self.do_command()
