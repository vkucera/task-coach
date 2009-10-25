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

iconlist = [
('copy', 'actions', 'editcopy', [16, 22, 32]),
('cut', 'actions', 'editcut', [16, 22, 32]),
('delete', 'actions', 'editdelete', [16, 22, 32]),
('edit', 'actions', 'edit', [16, 22, 32]),
('fileopen', 'actions', 'fileopen', [16, 22, 32]),
('fileopen_red', 'actions', 'fileopen_red', [16]),
('print', 'actions', 'fileprint', [16, 22, 32]),
('export', 'actions', 'fileexport', [16]),
('exportasics', 'mimetypes', 'vcalendar', [16]),
('exportashtml', 'mimetypes', 'html', [16]),
('exportascsv', 'mimetypes', 'txt', [16]),
('exportasvcal', 'mimetypes', 'vcard', [16]),
('close', 'actions', 'fileclose', [16]),
('exit', 'actions', 'exit', [16]),
('help', 'actions', 'help', [16]),
('info', 'actions', 'messagebox_info', [16]),
('cancel', 'actions', 'cancel', [16]),
('search', 'actions', 'viewmag', [16]),
('searchmenu', 'actions', 'searchmenu', [16]),
('markcompleted', 'apps', 'korganizer_todo', [16, 22, 32]),
('markuncompleted', 'actions', 'klipper_dock', [16, 32]),
('markuncompleted', 'actions', 'tool_clipboard', [22]),
('new', 'actions', 'filenew', [16, 22, 32]),
('newtmpl', 'actions', 'blend', [16, 22, 32]),
('newsub', 'actions', 'new_sub', [16, 22, 32]),
('on', 'actions', 'apply', [16]),
('paste', 'actions', 'editpaste', [16, 22, 32]),
('undo', 'actions', 'undo', [16, 22, 32]),
('redo', 'actions', 'redo', [16, 22, 32]),
('save', 'actions', 'filesave', [16, 22, 32]),
('saveas', 'actions', 'filesaveas', [16]),
('task', 'actions', 'ledblue', [16]),
('task_completed', 'actions', 'ledgreen', [16]),
('task_duesoon', 'actions', 'ledorange', [16]),
('task_inactive', 'actions', 'ledgrey', [16]),
('task_overdue', 'actions', 'ledred', [16]),
('taskcoach', 'apps', 'korganizer_todo', [16, 22, 32, 48, 64, 128]),
('tasks', 'filesystems', 'folder_blue', [16]),
('tasks_open', 'filesystems', 'folder_blue_open', [16]),
('tasks_completed', 'filesystems', 'folder_green', [16]),
('tasks_completed_open', 'filesystems', 'folder_green_open', [16]),
('tasks_duesoon', 'filesystems', 'folder_orange', [16]),
('tasks_duesoon_open', 'filesystems', 'folder_orange_open', [16]),
('tasks_inactive', 'filesystems', 'folder_grey', [16]),
('tasks_inactive_open', 'filesystems', 'folder_grey_open', [16]),
('tasks_overdue', 'filesystems', 'folder_red', [16]),
('tasks_overdue_open', 'filesystems', 'folder_red_open', [16]),
('listview', 'actions', 'view_detailed', [16, 22, 32]),
('treeview', 'actions', 'view_tree', [16, 22, 32]),
('start', 'actions', 'history', [16, 22, 32]),
('startmenu', 'actions', 'historymenu', [16, 22, 32]),
('stop', 'actions', 'history_clear', [16, 22, 32]),
('tick', 'apps', 'clock', [16, 128]),
('tack', 'apps', 'ktimer', [16, 128]),
('date', 'apps', 'date', [16, 22, 32]),
('filtercompletedtasks', 'actions', 'ledgreen_crossed', [16]),
('filterinactivetasks', 'actions', 'ledgrey_crossed', [16]),
('description', 'actions', 'pencil', [16, 22, 32]),
('restore', 'apps', 'kcmkwm', [16]),
('budget', 'apps', 'kcalc', [16, 22, 32]),
('progress', 'actions', 'finish', [16, 22, 32]),
('viewalltasks', 'apps', 'kreversi', [16]),
('viewnewviewer', 'actions', 'tab_new', [16]),
('squaremapviewer', 'actions', 'squaremap', [16]),
('timelineviewer', 'actions', 'timeline', [16]),
('activatenextviewer', 'actions', 'tab_advance_next', [16]),
('activatepreviousviewer', 'actions', 'tab_advance_prev', [16]),
('viewexpand', 'actions', 'edit_add', [16]),
('viewcollapse', 'actions', 'edit_remove', [16]),
('configure', 'actions', 'configure', [16]),
('language', 'apps', 'edu_languages', [22]),
('ascending', 'actions', 'up', [16]),
('descending', 'actions', 'down', [16]),
('ascending_with_status', 'actions', 'sort_ascending_with_status', [16]),
('descending_with_status', 'actions', 'sort_descending_with_status', [16]),
('category', 'filesystems', 'folder_download', [16, 22]),
('note', 'apps', 'knotes', [16, 22]),
('colorize', 'actions', 'colorize', [22]),
('windows', 'apps', 'window_list', [22]),
('email', 'apps', 'email', [16, 22]),
('behavior', 'actions', 'misc', [22]),
('sync', 'actions', 'kaboodleloop', [16, 22]),
('iphone', 'devices', 'pda', [22]),
('access', 'filesystems', 'www', [22]),
('attachment', 'actions', 'attach', [16, 22]),
('maxpriority', 'actions', '2uparrow', [16]),
('minpriority', 'actions', '2downarrow', [16]),
('incpriority', 'actions', '1uparrow', [16]),
('decpriority', 'actions', '1downarrow', [16]),
('uri', 'filesystems', 'www', [16]),
]

icons = {}

for pngName, type, filename, sizes in iconlist:
    for size in sizes:
        size = '%dx%d'%(size, size)
        icons['%s%s'%(pngName, size)] = 'nuvola/%s/%s/%s.png'%(size, type, filename)

