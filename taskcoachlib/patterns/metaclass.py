''' Module for metaclasses that are not widely recognized patterns. '''

class NumberedInstances(type):
    ''' A metaclass that numbers class instances. Use by defining the metaclass 
        of a class NumberedInstances, e.g.: 
        class Numbered:
            __metaclass__ = NumberedInstances 
        Each instance of class Numbered will have an attribute instanceNumber
        that is unique. '''
        
    count = dict()
        
    def __call__(class_, *args, **kwargs):
        kwargs['instanceNumber'] = NumberedInstances.count.setdefault(class_, 0)
        instance = super(NumberedInstances, class_).__call__(*args, **kwargs)
        NumberedInstances.count[class_] += 1
        return instance
    
