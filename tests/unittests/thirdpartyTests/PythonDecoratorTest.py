import test, sys

def protected(function):
    if function.func_code.co_argcount < 1:
        raise ValueError, \
            "method '%s' should take at least one argument"%function.__name__

    def wrapped(*args, **kwargs):
        callerFrameLocals = sys._getframe().f_back.f_locals
        if 'self' in callerFrameLocals and \
                isinstance(callerFrameLocals['self'], args[0].__class__):                          
            return function(*args, **kwargs)
        else:
            raise AttributeError, "attribute '%s' of %s instance" \
                " is protected"%(function.__name__, args[0].__class__.__name__)

    wrapped.__doc__ = function.__doc__
    wrapped.__name__ = function.__name__
    return wrapped


class SuperClass(object):
    def callProtectedMethodOnSubClass(self):
        self.protectedMethod()


class ClassWithProtectedMethod(SuperClass):
    def __init__(self, *args, **kwargs):
        super(ClassWithProtectedMethod, self).__init__(*args, **kwargs)
        self.protectedMethodCalled = False
        
    @protected
    def protectedMethod(self):
        self.protectedMethodCalled = True

    def callProtectedMethod(self):
        self.protectedMethod()


class SubClass(ClassWithProtectedMethod):
    def callProtectedMethodOnSelf(self):
        self.protectedMethod()
        
    def callProtectedMethodOnSuper(self):
        super(SubClass, self).protectedMethod()

        
class SubClassWithProtectedMethodOverriddenAsPublic(ClassWithProtectedMethod):
    def protectedMethod(self):
        self.overriddenProtectedMethodCalled = True


class SubClassWithProtectedMethodOverriddenAsProtected(ClassWithProtectedMethod):
    @protected
    def protectedMethod(self):
        self.overriddenProtectedMethodCalled = True

        
class ProtectedMethodTest(test.TestCase):
    def setUp(self):
        self.test = ClassWithProtectedMethod()
        
    def testClassCanCallItsOwnProtectedMethod(self):
        self.test.callProtectedMethod()
        self.failUnless(self.test.protectedMethodCalled)
        
    def testProtectedMethodCannotBeCalledByOtherObject(self):
        self.assertRaises(AttributeError, self.test.protectedMethod)
        
    def testProtectedMethodCannotBeCalledByFunction(self):
        self.assertRaises(AttributeError, lambda: self.test.protectedMethod())
        
    def testAttributeErrorMessage(self):
        try:
            self.test.protectedMethod()
        except AttributeError, instance:
            pass
        self.assertEqual("attribute 'protectedMethod' of %s instance" \
            " is protected"%self.test.__class__.__name__, str(instance))

class ProtectedMethodInSubClassTest(test.TestCase):
    def setUp(self):
        self.test = SubClass()

    def testSubclassCanCallProtectedMethodOnSelf(self):
        self.test.callProtectedMethodOnSelf()
        self.failUnless(self.test.protectedMethodCalled)
        
    def testSubclassCanCallProtectedMethodOnSuper(self):
        self.test.callProtectedMethodOnSuper()
        self.failUnless(self.test.protectedMethodCalled)

    def testProtectedMethodCannotBeCalledByOtherObject(self):
        self.assertRaises(AttributeError, self.test.protectedMethod)


class ProtectedMethodOverriddenAsPublicInSubClassTest(test.TestCase):
    def setUp(self):
        self.test = SubClassWithProtectedMethodOverriddenAsPublic()
        
    def testSubclassCanOverrideProtectedMethod(self):
        self.test.callProtectedMethod()
        self.failUnless(self.test.overriddenProtectedMethodCalled)
        self.failIf(self.test.protectedMethodCalled)
        
    def testOverriddenProtectedMethodIsNoLongerProtected(self):
        self.test.protectedMethod()
        self.failUnless(self.test.overriddenProtectedMethodCalled)
        

class ProtectedMethodOverriddenAsProtectedInSubClassTest(test.TestCase):
    def setUp(self):
        self.test = SubClassWithProtectedMethodOverriddenAsProtected()
        
    def testSubclassCanOverrideProtectedMethod(self):
        self.test.callProtectedMethod()
        self.failUnless(self.test.overriddenProtectedMethodCalled)
        self.failIf(self.test.protectedMethodCalled)
        
    def testOverriddenMethodIsProtectedWhenItIsDecoratedAsProtected(self):
        self.assertRaises(AttributeError, self.test.protectedMethod)
        

class ProtectedFunctionTest(test.TestCase):
    def testFunctionCannotBeProtected(self):
        def createProtectedFunction():
            @protected
            def function():
                pass
        self.assertRaises(ValueError, createProtectedFunction)