'''
Task Coach - Your friendly task manager
Copyright (C) 2011 Task Coach developers <developers@taskcoach.org>

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

import test, wx
from taskcoachlib.changes import ChangeMonitor
from taskcoachlib.domain.base import Object, CompositeObject
from taskcoachlib.patterns import ObservableList


class MonitorBaseTest(test.TestCase):
    klass = Object
    listClass = ObservableList

    def setUp(self):
        ChangeMonitor().reset()
        ChangeMonitor().monitorClass(self.klass)
        ChangeMonitor().monitorCollectionClass(self.listClass)

        self.list = self.listClass()
        self.obj = self.klass(subject=u'New object')
        self.list.append(self.obj)

    def tearDown(self):
        ChangeMonitor().unmonitorClass(self.klass)
        ChangeMonitor().unmonitorCollectionClass(self.listClass)


class MonitorObjectTest(MonitorBaseTest):
    def doTestAttributeChanged(self, name, value, initialValue, methodName=None):
        if methodName is None:
            methodName = name
        getattr(self.obj, 'set' + methodName[:1].upper() + methodName[1:])(initialValue)
        ChangeMonitor().resetChanges(self.obj)
        getattr(self.obj, 'set' + methodName[:1].upper() + methodName[1:])(value)
        self.assertEqual(ChangeMonitor().getChanges(self.obj), set([name]))

    def doTestAttributeDidNotChange(self, name, initialValue, methodName=None):
        if methodName is None:
            methodName = name
        getattr(self.obj, 'set' + methodName[:1].upper() + methodName[1:])(initialValue)
        ChangeMonitor().resetChanges(self.obj)
        getattr(self.obj, 'set' + methodName[:1].upper() + methodName[1:])(getattr(self.obj, methodName)())
        self.assertEqual(ChangeMonitor().getChanges(self.obj), set())

    def testSubjectChanged(self):
        self.doTestAttributeChanged('subject', 'New subject', 'Old subject')

    def testSubjectDidNotChange(self):
        self.doTestAttributeDidNotChange('subject', 'Subject')

    def testDescriptionChanged(self):
        self.doTestAttributeChanged('description', 'New description', 'Old description')

    def testDescriptionDidNotChange(self):
        self.doTestAttributeDidNotChange('description', 'Description')

    def testForegroundColorChanged(self):
        self.doTestAttributeChanged('appearance', (128, 128, 128), (64, 64, 64), 'foregroundColor')

    def testForegroundColorDidNotChange(self):
        self.doTestAttributeDidNotChange('appearance', (128, 128, 128), 'backgroundColor')

    def testBackgroundColorChanged(self):
        self.doTestAttributeChanged('appearance', (128, 128, 128), (64, 64, 64), 'backgroundColor')

    def testBackgroundColorDidNotChange(self):
        self.doTestAttributeDidNotChange('appearance', (128, 128, 128), 'backgroundColor')

    def testFontChanged(self):
        self.doTestAttributeChanged('appearance', 'dummy1', 'dummy2', 'font')

    def testFontDidNotChange(self):
        self.doTestAttributeDidNotChange('appearance', 'dummy', 'font')

    def testIconChanged(self):
        self.doTestAttributeChanged('appearance', 'foo', 'bar', 'icon')

    def testIconDidNotChange(self):
        self.doTestAttributeDidNotChange('appearance', 'foo', 'icon')

    def testSelectedIconChanged(self):
        self.doTestAttributeChanged('appearance', 'foo', 'bar', 'selectedIcon')

    def testSelectedIconDidNotChange(self):
        self.doTestAttributeDidNotChange('appearance', 'foo', 'selectedIcon')

    def testNewObject(self):
        obj = self.klass(subject=u'New')
        self.list.append(obj)
        self.assertEqual(ChangeMonitor().getChanges(obj), None)

    def testDeletedObject(self):
        self.list.remove(self.obj)
        self.failUnless(ChangeMonitor().isRemoved(self.obj))

    def testRemoveAdd(self):
        ChangeMonitor().resetChanges(self.obj)
        self.obj.setSubject('Foo')
        self.list.remove(self.obj)
        self.assertEqual(ChangeMonitor().getChanges(self.obj), None)
        self.list.append(self.obj)
        self.assertEqual(ChangeMonitor().getChanges(self.obj), set(['subject']))
        self.failIf(ChangeMonitor().isRemoved(self.obj))


class MonitorCompositeObjectTest(MonitorObjectTest):
    klass = CompositeObject

    def setUp(self):
        super(MonitorCompositeObjectTest, self).setUp()

        self.child = self.klass(subject=u'Child')
        self.obj.addChild(self.child)

    def testNewChild(self):
        child = self.obj.newChild(subject='Child')
        self.assertEqual(ChangeMonitor().getChanges(child), None)

    def testChangeChildSubject1(self):
        ChangeMonitor().resetChanges(self.obj)
        self.child.setSubject('Child subject')
        self.assertEqual(ChangeMonitor().getChanges(self.obj), set())

    def testChangeChildSubject2(self):
        ChangeMonitor().resetChanges(self.child)
        self.child.setSubject('Child subject')
        self.assertEqual(ChangeMonitor().getChanges(self.child), set(['subject']))

    def testExpansionChanged(self):
        ChangeMonitor().resetChanges(self.obj)
        self.obj.expand()
        self.assertEqual(ChangeMonitor().getChanges(self.obj), set(['expandedContexts']))

    def testAddChild(self):
        child = self.klass(subject='Child')
        self.list.append(child)
        ChangeMonitor().resetChanges(child)
        self.obj.addChild(child)
        self.assertEqual(ChangeMonitor().getChanges(child), set(['__parent__']))
