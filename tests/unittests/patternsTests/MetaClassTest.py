import patterns, test

class Numbered:
    __metaclass__ = patterns.NumberedInstances
    
    def __init__(self, instanceNumber=-1):
        self.instanceNumber = instanceNumber
    

class SubclassOfNumbered(Numbered):
    pass


class NumberedInstancesTests(object):
    ''' The tests below should work for a class with NumberedInstances as 
        metaclass as well as for a subclass of a class with NumberedInstances
        as metaclass. '''
        
    def testCounterIncreasesAfterEachInstantation(self):
        for count in range(3):
            self.assertEqual(count, patterns.NumberedInstances.count.get(self.classUnderTest, 0))
            self.classUnderTest()
        
    def testInstanceNumberIsSet(self):
        for count in range(3):
            self.assertEqual(count, self.classUnderTest().instanceNumber)


class NumberedInstancesTest(NumberedInstancesTests, test.TestCase):
    classUnderTest = Numbered


class SubclassOfNumberedInstancesTest(NumberedInstancesTests, test.TestCase):
    classUnderTest = SubclassOfNumbered

    def testSubclassInstancesHaveTheirOwnNumbers(self):
        SubclassOfNumbered()
        self.assertEqual(0, patterns.NumberedInstances.count.get(Numbered, 0))
        