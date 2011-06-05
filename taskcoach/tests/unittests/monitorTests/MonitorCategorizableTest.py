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

import test
from taskcoachlib.changes import ChangeMonitor
from taskcoachlib.domain.categorizable import CategorizableCompositeObject
from taskcoachlib.domain.category import Category
from taskcoachlib.patterns import ObservableList

class MonitorCategorizableTest(test.TestCase):
    def setUp(self):
        ChangeMonitor().reset()
        ChangeMonitor().monitorClass(CategorizableCompositeObject)
        ChangeMonitor().monitorCollectionClass(ObservableList)

        self.obj = CategorizableCompositeObject(subject=u'Object')
        self.list = ObservableList()
        self.list.append(self.obj)

        self.cat1 = Category(subject=u'Cat #1')
        self.cat2 = Category(subject=u'Cat #2')
        self.catList = ObservableList()
        self.catList.append(self.cat1)
        self.catList.append(self.cat2)

    def tearDown(self):
        ChangeMonitor().unmonitorClass(CategorizableCompositeObject)
        ChangeMonitor().unmonitorCollectionClass(ObservableList)

    def testAddCategory(self):
        ChangeMonitor().resetAllChanges()
        self.obj.addCategory(self.cat1)
        self.assertEqual(ChangeMonitor().getChanges(self.obj), set(['__categories__']))

    def testRemoveCategory(self):
        self.obj.addCategory(self.cat1)
        ChangeMonitor().resetAllChanges()
        self.obj.removeCategory(self.cat1)
        self.assertEqual(ChangeMonitor().getChanges(self.obj), set(['__categories__']))

    def testRemoveBadCategory(self):
        self.obj.addCategory(self.cat1)
        ChangeMonitor().resetAllChanges()
        self.obj.removeCategory(self.cat2)
        self.assertEqual(ChangeMonitor().getChanges(self.obj), set())
