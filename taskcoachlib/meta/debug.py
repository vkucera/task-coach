'''
Task Coach - Your friendly task manager
Copyright (C) 2008 Frank Niessink <frank@niessink.com>

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

import sys


def log_call(func):
    ''' Decorator for function calls that prints the function name,
        arguments and result to stdout. Usage:
        
        @log
        def function(arg):
            ...
    '''
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        sys.stdout.write('%s(%s, %s) -> %s\n'%(func.__name__, str(args), 
                                               str(kwargs), str(result)))
        return result
    return inner
