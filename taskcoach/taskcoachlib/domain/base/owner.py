'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>

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


def DomainObjectOwnerMetaclass(name, bases, ns):
    """This metaclass makes a class an owner for some domain
    objects. The __ownedType__ attribute of the class must be a
    string. For each type, the following methods will be added to the
    class (here assuming a type of 'Foo'):

      - __init__, __getstate__, __setstate__, __getcopystate__, __setcopystate__
      - addFoo, removeFoo, addFoos, removeFoos
      - setFoos, foos
      - foosChangedEventType
      - modificationEventTypes
      - __notifyObservers"""

    # This  metaclass is  a function  instead  of a  subclass of  type
    # because as we're replacing __init__, we don't want the metaclass
    # to be inherited by children.

    klass = type(name, bases, ns)

    def constructor(instance, *args, **kwargs):
        # NB: we use a simple list here. Maybe we should use a container type.
        setattr(instance,'_%s__%ss' % (name, klass.__ownedType__.lower()),
                kwargs.pop(klass.__ownedType__.lower() + 's', []))
        super(klass, instance).__init__(*args, **kwargs)

    klass.__init__ = constructor

    def changedEventType(class_):
        return '%s.%s' % (class_, klass.__ownedType__.lower())

    setattr(klass, '%ssChangedEventType' % klass.__ownedType__.lower(), 
            classmethod(changedEventType))
    
    def modificationEventTypes(class_):
        try:
            eventTypes = super(klass, class_).modificationEventTypes()
        except AttributeError:
            eventTypes = []
        return eventTypes + [changedEventType(class_)]
    
    klass.modificationEventTypes = classmethod(modificationEventTypes)

    def objects(instance):
        objects = getattr(instance, '_%s__%ss' % (name, klass.__ownedType__.lower()))
        return [object for object in objects if not object.isDeleted()]

    setattr(klass, '%ss' % klass.__ownedType__.lower(), objects)

    def notifyObservers(instance):
        instance.notifyObservers(patterns.Event(instance, 
                                                changedEventType(instance.__class__), 
                                                *objects(instance)))

    setattr(klass, '_%s__notifyObservers' % name, notifyObservers)

    def setObjects(instance, newObjects):
        if newObjects != objects(instance):
            setattr(instance, '_%s__%ss' % (name, klass.__ownedType__.lower()), 
                                            newObjects)
            notifyObservers(instance)

    setattr(klass, 'set%ss' % klass.__ownedType__, setObjects)

    def addObject(instance, object):
        getattr(instance, '_%s__%ss' % (name, klass.__ownedType__.lower())).append(object)
        notifyObservers(instance)

    setattr(klass, 'add%s' % klass.__ownedType__, addObject)

    def addObjects(instance, *objects):
        if objects:
            for object in objects:
                getattr(instance, '_%s__%ss' % (name, klass.__ownedType__.lower())).append(object)
            notifyObservers(instance)

    setattr(klass, 'add%ss' % klass.__ownedType__, addObjects)

    def removeObject(instance, object):
        getattr(instance, '_%s__%ss' % (name, klass.__ownedType__.lower())).remove(object)
        notifyObservers(instance)

    setattr(klass, 'remove%s' % klass.__ownedType__, removeObject)

    def removeObjects(instance, *objects):
        if objects:
            changed = False
            for object in objects:
                try:
                    getattr(instance, '_%s__%ss' % (name, klass.__ownedType__.lower())).remove(object)
                except ValueError:
                    pass
                else:
                    changed = True
            if changed:
                notifyObservers(instance)

    setattr(klass, 'remove%ss' % klass.__ownedType__, removeObjects)

    def getstate(instance):
        try:
            state = super(klass, instance).__getstate__()
        except AttributeError:
            state = dict()
        state[klass.__ownedType__.lower() + 's'] = getattr(instance, '_%s__%ss' % (name, klass.__ownedType__.lower()))[:]
        return state

    klass.__getstate__ = getstate

    def setstate(instance, state):
        try:
            super(klass, instance).__setstate__(state)
        except AttributeError:
            pass
        setObjects(instance, state[klass.__ownedType__.lower() + 's'])

    klass.__setstate__ = setstate

    def getcopystate(instance):
        try:
            state = super(klass, instance).__getcopystate__()
        except AttributeError:
            state = dict()
        state['%ss' % klass.__ownedType__.lower()] = [object.copy() for object in objects(instance)]
        return state

    klass.__getcopystate__ = getcopystate

    return klass
