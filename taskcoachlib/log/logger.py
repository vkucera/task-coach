import inspect, time, sys

def caller(nrHops=1):
        # Three hops: __caller -> __log -> wrapper -> real caller
        # Add one hop for this function
        nrHops += 1
        callerFrame = sys._getframe()
        for hopNr in range(nrHops):
            callerFrame = callerFrame.f_back
        callerName = callerFrame.f_code.co_name
        if 'self' in callerFrame.f_locals:
            callerName = '%s.%s'%(callerFrame.f_locals['self'].__class__.__name__, callerName)
        return callerName
    
class Logger:
    maxArgLength = 1000

    def watch(self, *scopes):
        for scope in scopes:
            for attr in scope.__dict__.keys():
                if attr in ['__str__', '__repr__']:
                    continue # don't wrap __str__ to prevent infinite recursion
                obj = getattr(scope, attr)
                if inspect.isroutine(obj) and inspect.getmodule(obj) == inspect.getmodule(scope):
                    setattr(scope, attr, self.__wrap(obj))
                elif inspect.isclass(obj):
                    self.watch(obj)

    def __wrap(self, func):
        def wrapper(*args, **kwargs):
            self.__log(func, *args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    
    def __caller(self):
        # Three hops: __caller -> __log -> wrapper -> real caller
        callerFrame = sys._getframe().f_back.f_back.f_back 
        callerName = callerFrame.f_code.co_name
        if 'self' in callerFrame.f_locals:
            callerName = '%s.%s'%(callerFrame.f_locals['self'].__class__.__name__, callerName)
        return callerName
    
    def __formatArg(self, arg):
        try:
            arg = str(arg)
        except:
            arg = '? (got exception)'
        if len(arg) > self.maxArgLength:
            arg = arg[:self.maxArgLength/2] + '...' + arg[-self.maxArgLength/2:]
        return arg
        
    def __formatArgs(self, args, kwargs):
        args = [self.__formatArg(arg) for arg in args]
        kwargs = ['%s=%s'%(key, self.__formatArg(value)) for key, value in kwargs.items()]
        return ', '.join(args + kwargs)
        
    def __formatFunc(self, func, args):
        try:
            className = args[0].__class__.__name__
            return '%s.%s'%(className, func.__name__)
        except:
            return func.__name__
             
    def __log(self, func, *args, **kwargs):
        print '%.4f: %s(%s) called from %s'%(time.clock(), 
            self.__formatFunc(func, args), self.__formatArgs(args, kwargs), 
            self.__caller())

