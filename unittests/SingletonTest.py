import test, patterns

class Singleton:
    __metaclass__ = patterns.Singleton
    pass

class SingletonTest(test.TestCase):
    def testCreation(self):
        singleton = Singleton()
        self.failUnless(isinstance(singleton, Singleton))

    def testCreateTwice(self):
        single1 = Singleton()
        single2 = Singleton()
        self.failUnless(single1 is single2)

    def testSingletonsCanHaveInit(self):
        class SingletonWithInit:
            __metaclass__ = patterns.Singleton
            def __init__(self):
                self.a = 1
        single = SingletonWithInit()
        self.assertEqual(1, single.a)

    def testSingletonInitCanHaveArgs(self):
        class SingletonWithInit:
            __metaclass__ = patterns.Singleton
            def __init__(self, arg):
                self.a = arg
        single = SingletonWithInit('Yo')
        self.assertEqual('Yo', single.a)

    def testSingletonInitIsOnlyCalledOnce(self):
        class SingletonWithInit:
            _count = 0
            __metaclass__ = patterns.Singleton
            def __init__(self):
                SingletonWithInit._count += 1
        single1 = SingletonWithInit()
        single2 = SingletonWithInit()
        self.assertEqual(1, SingletonWithInit._count)

class SingletonSubclassTest(test.TestCase):
    def testSubclassesAreSingletonsToo(self):
        class Sub(Singleton):
            pass
        sub1 = Sub()
        sub2 = Sub()
        self.failUnless(sub1 is sub2)

    def testDifferentSubclassesAreNotTheSameSingleton(self):
        class Sub1(Singleton):
            pass
        sub1 = Sub1()
        class Sub2(Singleton):
            pass
        sub2 = Sub2()
        self.failIf(sub1 is sub2)

    def testSubclassesCanHaveInit(self):
        class Sub(Singleton):
            def __init__(self):
                self.a = 1
        sub = Sub()
        self.assertEqual(1, sub.a)

    def testSubclassInitCanHaveArgs(self):
        class Sub(Singleton):
            def __init__(self, arg):
                pass
        try:
            sub = Sub('Yo')
        except TypeError:
            self.fail()

    def testSubclassInitIsOnlyCalledOnce(self):
        class Sub(Singleton):
            _count = 0
            def __init__(self):
                Sub._count += 1
        sub1 = Sub()
        sub2 = Sub()
        self.assertEqual(1, Sub._count)

