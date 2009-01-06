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

def log_call(traceback_depth):
    ''' Decorator for function calls that prints the function name,
        arguments and result to stdout. Usage:
        
        @log_call(traceback_depth)
        def function(arg):
            ...
    '''
    # Import here instead of at the module level to prevent unnecessary 
    # inclusion of the inspect module when packaging the application:
    import inspect 

    def outer(func):        
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            write = sys.stdout.write
            for frame in inspect.stack(context=2)[traceback_depth:0:-1]:
                write(format_traceback(frame))
            try:
                write('%s(%s, %s) -> %s\n'%(func.__name__, unicode(args), 
                                        unicode(kwargs), unicode(result)))
            except:
                write('%s(...) -> %s\n'%(func.__name__, unicode(result)))
            write('===\n')
            return result
        return inner
    return outer

def format_traceback(frame):
    result = []
    filename, lineno, caller, context = frame[1:5]
    result.append('  File "%s", line %s, in %s'%(filename, lineno, caller))
    for line in context:
        result.append(line[:-1])
    return '\n'.join(result) + '\n'   
    