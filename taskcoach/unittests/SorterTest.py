import test, task, task.sorter, patterns, date, effort

class Node(patterns.Observable):
    def __init__(self, name, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self._name = name

    def __cmp__(self, other):
        return cmp(self._name, other._name)

    def __repr__(self):
        return self._name

    def setName(self, name):
        self._name = name
        self.notifyObservers(patterns.observer.Notification(self))


class SorterTest(test.TestCase):
    def setUp(self):
        a = self.a = Node('a')
        b = self.b = Node('b')
        c = self.c = Node('c')
        d = self.d = Node('d')
        self.list = patterns.ObservableObservablesList([d, b, c, a])
        self.sorter = task.sorter.Sorter(self.list)

    def testLength(self):
        self.assertEqual(4, len(self.sorter))

    def testGetItem(self):
        self.assertEqual(self.a, self.sorter[0])

    def testOrder(self):
        self.assertEqual([self.a, self.b, self.c, self.d], list(self.sorter))

    def testRemoveItem(self):
        self.sorter.remove(self.c)
        self.assertEqual(3, len(self.sorter))
        self.assertEqual([self.a, self.b, self.d], list(self.sorter))
        self.assertEqual([self.d, self.b, self.a], self.list)

    def testAppend(self):
        e = Node('e')
        self.list.append(e)
        self.assertEqual(5, len(self.sorter))
        self.assertEqual(e, self.sorter[-1])

    def testChange(self):
        self.a.setName('z')
        self.assertEqual([self.b, self.c, self.d, self.a], list(self.sorter))


class NodeWithChildren(Node):
    def __init__(self, name, parent=None, *args, **kwargs):
        super(NodeWithChildren, self).__init__(name, *args, **kwargs)
        self._children = []
        self._parent = parent
        if parent:
            parent.addChild(self)

    def addChild(self, child):
        self._children.append(child)

    def removeChild(self, child):
        self._children.remove(child)

    def delete(self):
        if self._parent:
            self._parent.removeChild(self)

    def children(self):
        return self._children

    def parent(self):
        return self._parent


class DummyList(patterns.ObservableObservablesList):
    def rootTasks(self):
        return [task for task in self if task.parent() is None]
       

class DepthFirstSorterTest(test.TestCase):
    def setUp(self):
        self.parent1 = NodeWithChildren('1')
        self.child1 = NodeWithChildren('1.1', self.parent1)
        self.grandchild = NodeWithChildren('1.1.1', self.child1)
        self.child2 = NodeWithChildren('1.2', self.parent1)
        self.parent2 = NodeWithChildren('2')
        self.list = DummyList([self.parent2, self.child2, 
            self.parent1, self.child1, self.grandchild])
        self.sorter = task.sorter.DepthFirstSorter(self.list)

    def testLength(self):
        self.assertEqual(len(self.list), len(self.sorter))

    def testGetItem(self):
        self.assertEqual(self.parent1, self.sorter[0])
        self.assertEqual(self.child1, self.sorter[1])
        self.assertEqual(self.grandchild, self.sorter[2])
        self.assertEqual(self.child2, self.sorter[3])
        self.assertEqual(self.parent2, self.sorter[4])

    def testRemoveItem(self):
        self.grandchild.delete()
        self.sorter.remove(self.grandchild)
        self.assertEqual(4, len(self.sorter))
        self.assertEqual(self.parent2, self.sorter[-1])
        self.assertEqual([self.parent2, self.child2, self.parent1,  
            self.child1], self.list)

    def testAppendItem(self):
        node = NodeWithChildren('1.1.1.1', self.grandchild)
        self.list.append(node)
        self.assertEqual(6, len(self.sorter))
        self.assertEqual(node, self.sorter[3])

    def testMarkCompleted(self):
        self.child2.setName('1.0')
        self.assertEqual([self.parent1, self.child2, self.child1,
            self.grandchild, self.parent2], list(self.sorter))

class EffortSorterTest(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.sorter = effort.EffortSorter(self.effortList)
        self.task = task.Task()
        self.task.addEffort(effort.Effort(self.task,
            date.DateTime(2004,2,1), date.DateTime(2004,2,2)))
        self.task.addEffort(effort.Effort(self.task,
            date.DateTime(2004,1,1), date.DateTime(2004,1,2)))
        self.taskList.append(self.task)

    def testDescending(self):
        self.assertEqual(self.effortList[0], self.sorter[1])
        self.assertEqual(self.effortList[1], self.sorter[0])

    def testResort(self):
        self.effortList[1].setStart(date.DateTime(2004,3,1))
        self.assertEqual(self.effortList[0], self.sorter[0])
        self.assertEqual(self.effortList[1], self.sorter[1])
