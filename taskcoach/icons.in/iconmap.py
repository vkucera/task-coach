'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Frank Niessink <frank@niessink.com>

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
# These icons are named after their function:
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
('markcompleted', 'apps', 'korganizer_todo', [16, 22, 32]),
('markuncompleted', 'actions', 'klipper_dock', [16, 32]),
('markuncompleted', 'actions', 'tool_clipboard', [22]),
('new', 'actions', 'filenew', [16, 22, 32]),
('newtmpl', 'actions', 'blend', [16, 22, 32]),
('newsub', 'actions', 'new_sub', [16, 22, 32]),
('paste', 'actions', 'editpaste', [16, 22, 32]),
('undo', 'actions', 'undo', [16, 22, 32]),
('redo', 'actions', 'redo', [16, 22, 32]),
('save', 'actions', 'filesave', [16, 22, 32]),
('saveas', 'actions', 'filesaveas', [16]),
('taskcoach', 'apps', 'korganizer_todo', [16, 22, 32, 48, 64, 128]),
('listview', 'actions', 'view_detailed', [16, 22, 32]),
('treeview', 'actions', 'view_tree', [16, 22, 32]),
('startmenu', 'actions', 'historymenu', [16, 22, 32]),
('stop', 'actions', 'history_clear', [16, 22, 32]),
('tick', 'apps', 'clock', [16, 128]),
('tack', 'apps', 'ktimer', [16, 128]),
('filtercompletedtasks', 'actions', 'ledgreen_faded', [16]),
('filterinactivetasks', 'actions', 'ledgrey_faded', [16]),
('restore', 'apps', 'kcmkwm', [16]),
('progress', 'actions', 'finish', [16, 22, 32]),
('viewalltasks', 'apps', 'kreversi', [16]),
('viewnewviewer', 'actions', 'tab_new', [16]),
('squaremapviewer', 'actions', 'squaremap', [16]),
('timelineviewer', 'actions', 'timeline', [16]),
('activatenextviewer', 'actions', 'tab_advance_next', [16]),
('activatepreviousviewer', 'actions', 'tab_advance_prev', [16]),
('viewexpand', 'actions', 'edit_add', [16]),
('viewcollapse', 'actions', 'edit_remove', [16]),
('ascending', 'actions', 'up', [16]),
('descending', 'actions', 'down', [16]),
('ascending_with_status', 'actions', 'sort_ascending_with_status', [16]),
('descending_with_status', 'actions', 'sort_descending_with_status', [16]),
('windows', 'apps', 'window_list', [22]),
('iphone', 'devices', 'pda', [22]),
('access', 'filesystems', 'www', [22]),
('maxpriority', 'actions', '2uparrow', [16]),
('minpriority', 'actions', '2downarrow', [16]),
('incpriority', 'actions', '1uparrow', [16]),
('decpriority', 'actions', '1downarrow', [16]),
('prev', 'actions', '1leftarrow', [16, 22]),
('next', 'actions', '1rightarrow', [16, 22]),

# These icons are named after what they display:
('arrows_looped_icon', 'actions', 'kaboodleloop', [16, 22]),
('calculator_icon', 'apps', 'kcalc', [16, 22, 32]),
('calendar_icon', 'apps', 'date', [16, 22, 32]),
('checkmark_green_icon', 'actions', 'apply', [16]),
('clock_icon', 'actions', 'history', [16, 22, 32]),
('cogwheel_icon', 'actions', 'misc', [16, 22]),
('cross_red_icon', 'actions', 'cancel', [16]),
('earth_blue_icon', 'filesystems', 'www', [16]),
('envelope_icon', 'apps', 'email', [16, 22]),
('folder_blue_icon', 'filesystems', 'folder_blue', [16]),
('folder_blue_arrow_icon', 'filesystems', 'folder_download', [16, 22]),
('folder_blue_open_icon', 'filesystems', 'folder_blue_open', [16]),
('folder_green_icon', 'filesystems', 'folder_green', [16]),
('folder_green_open_icon', 'filesystems', 'folder_green_open', [16]),
('folder_orange_icon', 'filesystems', 'folder_orange', [16]),
('folder_orange_open_icon', 'filesystems', 'folder_orange_open', [16]),
('folder_grey_icon', 'filesystems', 'folder_grey', [16]),
('folder_grey_open_icon', 'filesystems', 'folder_grey_open', [16]),
('folder_red_icon', 'filesystems', 'folder_red', [16]),
('folder_red_open_icon', 'filesystems', 'folder_red_open', [16]),
('led_blue_icon', 'actions', 'ledblue', [16]),
('led_blue_questionmark_icon', 'actions', 'help', [16]),
('led_blue_information_icon', 'actions', 'messagebox_info', [16]),
('led_green_icon', 'actions', 'ledgreen', [16]),
('led_orange_icon', 'actions', 'ledorange', [16]),
('led_grey_icon', 'actions', 'ledgrey', [16]),
('led_red_icon', 'actions', 'ledred', [16]),
('magnifier_glass_dropdown_icon', 'actions', 'searchmenu', [16]),
('magnifier_glass_icon', 'actions', 'viewmag', [16]),
('note_icon', 'apps', 'knotes', [16, 22]),
('palette_icon', 'actions', 'colorize', [16, 22, 32]),
('paperclip_icon', 'actions', 'attach', [16, 22]),
('pencil_icon', 'actions', 'pencil', [16, 22, 32]),
('people_talking_icon', 'apps', 'edu_languages', [16, 22]),
('wrench_icon', 'actions', 'configure', [16]),
]

icons = {}

for pngName, type, filename, sizes in iconlist:
    for size in sizes:
        size = '%dx%d'%(size, size)
        icons['%s%s'%(pngName, size)] = 'nuvola/%s/%s/%s.png'%(size, type, filename)

