import test, patterns, config
import domain.task as task
import domain.date as date


class TestFilter(task.filter.Filter):
    def filter(self, items):
        return [item for item in items if item > 'b']


class FilterTests(object):
    def setUp(self):
        self.observable = self.collectionClass(['a', 'b', 'c', 'd'])
        self.filter = TestFilter(self.observable)

    def testLength(self):
        self.assertEqual(2, len(self.filter))

    def testContents(self):
        self.failUnless('c' in self.filter and 'd' in self.filter)

    def testRemoveItem(self):
        self.filter.remove('c')
        self.assertEqual(1, len(self.filter))
        self.failUnless('d' in self.filter)
        self.assertEqual(['a', 'b', 'd'], self.observable)

    def testNotification(self):
        self.observable.append('e')
        self.assertEqual(3, len(self.filter))
        self.failUnless('e' in self.filter)

        
class FilterListTest(FilterTests, test.TestCase):
    collectionClass = patterns.ObservableList


class FilterSetTest(FilterTests, test.TestCase):
    collectionClass = patterns.ObservableSet
    
    
class DummyFilter(task.filter.Filter):
    def filter(self, items):
        return items
    
    def test(self):
        self.testcalled = 1


class StackedFilterTest(test.TestCase):
    def setUp(self):
        self.list = patterns.ObservableList(['a', 'b', 'c', 'd'])
        self.filter1 = DummyFilter(self.list)
        self.filter2 = TestFilter(self.filter1)

    def testDelegation(self):
        self.filter2.test()
        self.assertEqual(1, self.filter1.testcalled)


class ViewFilterTest(test.TestCase):
    def setUp(self):
        self.list = task.TaskList()
        self.settings = config.Settings(load=False)
        self.filter = task.filter.ViewFilter(self.list, settings=self.settings)
        self.task = task.Task(subject='task')
        self.dueToday = task.Task(subject='due today', dueDate=date.Today())
        self.dueTomorrow = task.Task(subject='due tomorrow', 
            dueDate=date.Tomorrow())
        self.dueYesterday = task.Task(subject='due yesterday', 
            dueDate=date.Yesterday())
        self.child = task.Task(subject='child')

    def testCreate(self):
        self.assertEqual(0, len(self.filter))

    def testAddTask(self):
        self.filter.append(self.task)
        self.assertEqual(1, len(self.filter))
        
    def testViewActiveTasks(self):
        self.filter.append(self.task)
        self.settings.set('view', 'activetasks', 'False')
        self.assertEqual(0, len(self.filter))

    def testFilterCompletedTask(self):
        self.task.setCompletionDate()
        self.filter.append(self.task)
        self.assertEqual(1, len(self.filter))
        self.settings.set('view', 'completedtasks', 'False')
        self.assertEqual(0, len(self.filter))
        
    def testFilterCompletedTask_RootTasks(self):
        self.task.setCompletionDate()
        self.filter.append(self.task)
        self.settings.set('view', 'completedtasks', 'False')
        self.assertEqual(0, len(self.filter.rootItems()))

    def testFilterDueToday(self):
        self.filter.extend([self.task, self.dueToday])
        self.assertEqual(2, len(self.filter))
        self.settings.set('view', 'tasksdue', 'Today')
        self.assertEqual(1, len(self.filter))
    
    def testFilterDueToday_ShouldIncludeOverdueTasks(self):
        self.filter.append(self.dueYesterday)
        self.settings.set('view', 'tasksdue', 'Today')
        self.assertEqual(1, len(self.filter))

    def testFilterDueToday_ShouldIncludeCompletedTasks(self):
        self.filter.append(self.dueToday)
        self.dueToday.setCompletionDate()
        self.settings.set('view', 'tasksdue', 'Today')
        self.assertEqual(1, len(self.filter))

    def testFilterDueTomorrow(self):
        self.filter.extend([self.task, self.dueTomorrow, self.dueToday])
        self.assertEqual(3, len(self.filter))
        self.settings.set('view', 'tasksdue', 'Tomorrow')
        self.assertEqual(2, len(self.filter))
    
    def testFilterDueWeekend(self):
        dueNextWeek = task.Task(dueDate=date.Today() + \
            date.TimeDelta(days=8))
        self.filter.extend([self.dueToday, dueNextWeek])
        self.settings.set('view', 'tasksdue', 'Workweek')
        self.assertEqual(1, len(self.filter))


class ViewFilterInTreeModeTest(test.TestCase):
    def setUp(self):
        self.list = task.TaskList()
        self.settings = config.Settings(load=False)
        self.filter = task.filter.ViewFilter(self.list, settings=self.settings, treeMode=True)
        self.task = task.Task()
        self.dueToday = task.Task(dueDate=date.Today())
        self.dueTomorrow = task.Task(dueDate=date.Tomorrow())
        self.dueYesterday = task.Task(dueDate=date.Yesterday())
        self.child = task.Task()
        
    def testCreate(self):
        self.assertEqual(0, len(self.filter))
        
    def testAddTask(self):
        self.filter.append(self.task)
        self.assertEqual(1, len(self.filter))

    def testFilterDueToday(self):
        self.task.addChild(self.dueToday)
        self.list.append(self.task)
        self.settings.set('view', 'tasksdue', 'Today')
        self.assertEqual(2, len(self.filter))
        
    def testFilterOverDueTasks(self):
        self.task.addChild(self.dueYesterday)
        self.list.append(self.task)
        self.settings.set('view', 'overduetasks', 'False')
        self.assertEqual(1, len(self.filter))
        
        
class CompositeFilterTest(test.wxTestCase):
    def setUp(self):
        self.list = task.TaskList()
        self.settings = config.Settings(load=False)
        self.filter = task.filter.CompositeFilter(self.list, 
            settings=self.settings)
        self.task = task.Task(subject='task')
        self.child = task.Task(subject='child')
        self.task.addChild(self.child)
        self.filter.append(self.task)

    def testInitial(self):
        self.assertEqual(2, len(self.filter))
                
    def testTurnOn(self):
        self.settings.set('view', 'compositetasks', 'False')
        self.assertEqual([self.child], list(self.filter))

    def testTurnOff(self):
        self.settings.set('view', 'compositetasks', 'False')
        self.settings.set('view', 'compositetasks', 'True')
        self.assertEqual(2, len(self.filter))
                
    def testAddChild(self):
        self.settings.set('view', 'compositetasks', 'False')
        grandChild = task.Task(subject='grandchild')
        self.list.append(grandChild)
        self.child.addChild(grandChild)
        self.assertEqual([grandChild], list(self.filter))

    def testRemoveChild(self):
        self.settings.set('view', 'compositetasks', 'False')
        self.list.remove(self.child)
        self.assertEqual([self.task], list(self.filter))

    def _addTwoGrandChildren(self):
        self.grandChild1 = task.Task(subject='grandchild 1')
        self.grandChild2 = task.Task(subject='grandchild 2')
        self.child.addChild(self.grandChild1)
        self.child.addChild(self.grandChild2)
        self.list.extend([self.grandChild1, self.grandChild2])

    def testAddTwoChildren(self):
        self.settings.set('view', 'compositetasks', 'False')
        self._addTwoGrandChildren()
        self.assertEqual([self.grandChild1, self.grandChild2], 
            list(self.filter))

    def testRemoveTwoChildren(self):
        self._addTwoGrandChildren()
        self.settings.set('view', 'compositetasks', 'False')
        self.list.removeItems([self.grandChild1, self.grandChild2])
        self.assertEqual([self.child], list(self.filter))


class SearchFilterTest(test.TestCase):
    def setUp(self):
        self.parent = task.Task(subject='ABC')
        self.child = task.Task(subject='DEF')
        self.parent.addChild(self.child)
        self.list = task.TaskList([self.parent, self.child])
        self.settings = config.Settings(load=False)
        self.filter = task.filter.SearchFilter(self.list, settings=self.settings)

    def setSearchString(self, searchString):
        self.settings.set('view', 'tasksearchfilterstring', searchString)
        
    def testNoMatch(self):
        self.setSearchString('XYZ')
        self.assertEqual(0, len(self.filter))

    def testMatch(self):
        self.setSearchString('AB')
        self.assertEqual(1, len(self.filter))

    def testMatchIsCaseInSensitiveByDefault(self):
        self.setSearchString('abc')
        self.assertEqual(1, len(self.filter))

    def testMatchCaseInsensitive(self):
        self.settings.set('view', 'tasksearchfiltermatchcase', 'True')
        self.setSearchString('abc')
        self.assertEqual(0, len(self.filter))

    def testMatchWithRE(self):
        self.setSearchString('a.c')
        self.assertEqual(1, len(self.filter))

    def testMatchWithEmptyString(self):
        self.setSearchString('')
        self.assertEqual(2, len(self.filter))

    def testMatchChildDoesNotSelectParentWhenNotInTreeMode(self):
        self.setSearchString('DEF')
        self.assertEqual(1, len(self.filter))

    def testMatchChildAlsoSelectsParentWhenInTreeMode(self):
        self.filter.setTreeMode(True)
        self.setSearchString('DEF')
        self.assertEqual(2, len(self.filter))
        
    def testMatchChildDoesNotSelectParentWhenChildNotInList(self):
        self.list.remove(self.child) 
        self.parent.addChild(self.child) # simulate a child that has been filtered 
        self.setSearchString('DEF')
        self.assertEqual(0, len(self.filter))

    def testAddTask(self):
        self.setSearchString('XYZ')
        taskXYZ = task.Task(subject='subject with XYZ')
        self.list.append(taskXYZ)
        self.assertEqual([taskXYZ], list(self.filter))

    def testRemoveTask(self):
        self.setSearchString('DEF')
        self.list.remove(self.child)
        self.failIf(self.filter)


class CategoryFilterHelpers(object):
    def setFilterOnAnyCategory(self):
        self.settings.set('view', 'taskcategoryfiltermatchall', 'False')
        
    def setFilterOnAllCategories(self):
        self.settings.set('view', 'taskcategoryfiltermatchall', 'True')
 
    def addCategory(self, category):
        filteredCategories = self.filteredCategories()
        if category not in filteredCategories:
            filteredCategories.append(category)
            self.settings.setlist('view', 'taskcategoryfilterlist', 
                                  filteredCategories)
    
    def removeCategory(self, category):
        filteredCategories = self.filteredCategories()
        if category in filteredCategories:
            filteredCategories.remove(category)
            self.settings.setlist('view', 'taskcategoryfilterlist', 
                                  filteredCategories)    

    def removeAllCategories(self):
        self.settings.setlist('view', 'taskcategoryfilterlist', [])
        
    def filteredCategories(self):
        return self.settings.getlist('view', 'taskcategoryfilterlist')
    
    
class CategoryFilterFixtureAndCommonTests(CategoryFilterHelpers):
    def setUp(self):
        self.parent = task.Task()
        self.parent.addCategory('parent')
        self.child = task.Task()
        self.child.addCategory('child')
        self.parent.addChild(self.child)
        self.list = task.TaskList([self.parent, self.child])
        self.settings = config.Settings(load=False)
        self.filter = task.filter.CategoryFilter(self.list,
            settings=self.settings, treeMode=self.treeMode)
                              
    def testInitial(self):
        self.assertEqual(2, len(self.filter))
    
    def testFilterOnCategoryNotPresent(self):
        self.addCategory('test')
        self.assertEqual(0, len(self.filter))
 
    def testFilterOnCategoryParent(self):
        self.addCategory('parent')
        self.assertEqual(2, len(self.filter))

    def testRemoveCategory(self):
        self.addCategory('parent')
        self.removeCategory('parent')
        self.assertEqual(2, len(self.filter))

    def testFilteredCategories(self):
        self.addCategory('test')
        self.failUnless('test' in self.filteredCategories())
            
    def testClearFilter(self):
        self.addCategory('parent')
        self.removeAllCategories()
        self.assertEqual(2, len(self.filter))

    def testRemoveCategoryThatIsNotCurrentlyUsed(self):
        self.removeCategory('parent')
        self.assertEqual(2, len(self.filter))

    def testFilterOnAnyCategory(self):
        self.setFilterOnAnyCategory()
        self.addCategory('parent')
        self.addCategory('child')
        self.assertEqual(2, len(self.filter))

    def testFilterOnAnyCategory_NoTasksMatch(self):
        self.setFilterOnAnyCategory()
        self.addCategory('test')
        self.addCategory('another')
        self.assertEqual(0, len(self.filter))

    def testFilterOnAllCategories_NoTasksMatch(self):
        self.setFilterOnAllCategories()
        self.addCategory('test')
        self.addCategory('child')
        self.assertEqual(0, len(self.filter))

    def testFilterOnAnyCategory_NoCategoriesSelected(self):
        self.setFilterOnAnyCategory()
        self.assertEqual(2, len(self.filter))

    def testFilterOnAllCategories_NoCategoriesSelected(self):
        self.setFilterOnAllCategories()
        self.assertEqual(2, len(self.filter))
                    

class CategoryFilterInListModeTest(CategoryFilterFixtureAndCommonTests, 
                                   test.TestCase):
    treeMode = False   
       
    def testFilterOnCategoryChild(self):
        self.addCategory('child')
        self.assertEqual(1, len(self.filter))
        self.failUnless(self.child in self.filter)
        
    def testFilterOnAllCategories(self):
        self.setFilterOnAllCategories()
        self.addCategory('parent')
        self.addCategory('child')
        self.assertEqual(1, len(self.filter))
        self.failUnless(self.child in self.filter)


class CategoryFilterInTreeModeTest(CategoryFilterFixtureAndCommonTests, 
                                   test.TestCase):
    treeMode = True

    def testFilterOnCategoryChild(self):
        self.addCategory('child')
        self.assertEqual(2, len(self.filter))

    def testFilterOnAllCategories(self):
        self.setFilterOnAllCategories()
        self.addCategory('parent')
        self.addCategory('child')
        self.assertEqual(2, len(self.filter))
            
                
class OriginalLengthTest(test.TestCase, CategoryFilterHelpers):
    def setUp(self):
        self.list = task.TaskList()
        self.settings = config.Settings(load=False)
        self.filter = task.filter.CategoryFilter(self.list,
                                                 settings=self.settings)
        
    def testEmptyList(self):
        self.assertEqual(0, self.filter.originalLength())
        
    def testNoFilter(self):
        self.list.append(task.Task())
        self.assertEqual(1, self.filter.originalLength())
        
    def testFilter(self):
        aTask = task.Task()
        aTask.addCategory('test')
        self.list.append(aTask)
        self.addCategory('nottest')
        self.assertEqual(0, len(self.filter))
        self.assertEqual(1, self.filter.originalLength())

     
