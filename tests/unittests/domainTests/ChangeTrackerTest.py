'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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
from taskcoachlib.domain import base


class ChangeTrackerTest(test.TestCase):
    def setUp(self):
        self.collection = base.Collection()
        self.startTracking()
        self.object = base.CompositeObject()
        
    def startTracking(self):
        self.tracker = base.ChangeTracker(self.collection)
        
    def testTrackerHasNotObservedAnyAdditionsByDefault(self):
        self.failIf(self.tracker.added())
        
    def testTrackerHasNotObservedAnyRemovalsByDefault(self):
        self.failIf(self.tracker.removed())
        
    def testTrackerHasNotObservedAnyModificationsByDefault(self):
        self.failIf(self.tracker.modified())
        
    def testAddItem(self):
        self.collection.append(self.object)
        self.assertEqual(set([self.object.id()]), self.tracker.added())
        
    def testRemoveItem(self):
        self.collection.append(self.object)
        self.startTracking()
        self.collection.remove(self.object)
        self.assertEqual(set([self.object.id()]), self.tracker.removed())
        
    def testModifyItem(self):
        self.collection.append(self.object)
        self.startTracking()
        self.object.setSubject('New subject')
        self.assertEqual(set([self.object.id()]), self.tracker.modified())
        
    def testModifyAddedItem(self):
        self.collection.append(self.object)
        self.object.setSubject('New subject')
        self.failIf(self.tracker.modified())
        
    def testRemoveAddedItem(self):
        self.collection.append(self.object)
        self.collection.remove(self.object)
        self.failIf(self.tracker.removed())
        self.failIf(self.tracker.added())
        
    def testRemoveModifiedItem(self):
        self.collection.append(self.object)
        self.startTracking()
        self.object.setSubject('New subject')
        self.collection.remove(self.object)
        self.failIf(self.tracker.modified())
        
    def testRemoveModificationObservationWhenItemIsRemovedFromCollection(self):
        self.collection.append(self.object)
        self.startTracking()
        self.collection.remove(self.object)
        self.object.setSubject('New subject')
        self.failIf(self.tracker.modified())
        
