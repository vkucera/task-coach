import inspect, patterns, time, sys

class Logger:
    __metaclass__ = patterns.Singleton
    
    def watch(self, scope):
        for attr in scope.__dict__.keys():
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
    
    def __formatArgs(self, args, kwargs):
        args = [str(arg) for arg in args]
        kwargs = ['%s=%s'%(key, value) for key, value in kwargs.items()]
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

