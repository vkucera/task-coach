import test, task, date
import cStringIO as StringIO


class TaskReaderTestCase(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.taskReader = task.TaskReader(self.fd)

    def write(self):
        raise NotImplementedError

    def writeAndRead(self):
        self.write()
        self.fd.reset()
        return self.taskReader.read()


class TaskReaderVersion1Test(TaskReaderTestCase):    
    def write(self):
        self.fd.write('.tsk format version 1\n')
        
    def testReadEmptyList(self):
        tasks = self.writeAndRead()
        self.assertEqual([], tasks)

    def testVersion(self):    
        tasks = self.writeAndRead()
        self.assertEqual('.tsk format version 1', self.taskReader.version)


class TestReaderVersion2Test(TaskReaderTestCase):        
    def write(self):
        self.fd.write('.tsk format version 2\n')
        self.fd.write('Task 1,,id1,None,2004-10-10,None,[]\n')
        self.fd.write('Task 2,,id2,None,2004-10-10,None,[]\n')
        self.fd.write("Task 3,,id3,None,2004-10-10,None,['id2']\n")
        
    def testDescription(self):
        tasks = self.writeAndRead()
        self.assertEqual('Task 1', tasks[0].subject())
        
    def testChildren(self):
        tasks = self.writeAndRead()
        self.assertEqual(1, len(tasks[1].children()))


class TestReaderVersion3Test(TaskReaderTestCase):
    def write(self):
        self.fd.write('.tsk format version 3\n')
        self.fd.write('Task 1,,id,None,2004-10-10,None,[],0\n')
        self.fd.write('Task 2,,id,None,2004-10-10,None,[],1\n')
        self.fd.write('"(2005, 1, 9, 23, 23, 38, 6, 9, -1)","(2005, 1, 9, 23, 23, 39, 6, 9, -1)"\n')
        self.fd.write('Task 3,,id,None,2004-10-10,None,[],2\n')
        self.fd.write('"(2005, 1, 9, 23, 23, 38, 6, 9, -1)","(2005, 1, 9, 23, 23, 39, 6, 9, -1)"\n')
        self.fd.write('"(2005, 1, 9, 23, 23, 40, 6, 9, -1)","(2005, 1, 9, 23, 23, 41, 6, 9, -1)"\n')

    def testSubject(self):
        tasks = self.writeAndRead()
        self.assertEqual('Task 1', tasks[0].subject())
        
    def testEffort(self):
        tasks = self.writeAndRead()
        for task in tasks:
            for effort in task.efforts():
                self.assertEqual(date.TimeDelta(seconds=1), effort.duration())
                self.assertEqual(task, effort.task())

        

class TestReaderVersion4Test(TaskReaderTestCase):
    def write(self):
        self.fd.write('.tsk format version 4\n')
        self.fd.write("New task,,24247504:1106497024.73,None,2005-01-23,None,['24285680:1106497028.38']\n")
        self.fd.write("New subtask,,24285680:1106497028.38,None,2005-01-23,None,[]\n")
        self.fd.write("effort:\n")
        self.fd.write('24247504:1106497024.73,"(2005, 1, 23, 17, 17, 12, 6, 23, -1)","(2005, 1, 23, 17, 17, 13, 6, 23, -1)"\n')
        self.fd.write('24285680:1106497028.38,"(2005, 1, 23, 17, 17, 15, 6, 23, -1)","(2005, 1, 23, 17, 17, 16, 6, 23, -1)"\n')
        
    def testSubject(self):
        tasks = self.writeAndRead()
        self.assertEqual('New task', tasks[0].subject())
        
    def testEffort(self):
        tasks = self.writeAndRead()
        for task in tasks:
            self.assertEqual(1, len(task.efforts()))
        
    def testTasks(self):
        tasks = self.writeAndRead()
        self.assertEqual(1, len(tasks))
        self.assertEqual(1, len(tasks[0].children()))

class TestReaderVersion5Test(TaskReaderTestCase):
    def write(self):
        self.fd.write('.tsk format version 5\n')
        self.fd.write("New task,,24247504:1106497024.73,None,2005-01-23,None,['24285680:1106497028.38']\n")
        self.fd.write("New subtask,,24285680:1106497028.38,None,2005-01-23,None,[]\n")
        self.fd.write("effort:\n")
        self.fd.write('24247504:1106497024.73,"(2005, 1, 23, 17, 17, 12, 6, 23, -1)","(2005, 1, 23, 17, 17, 13, 6, 23, -1)",description\n')
        self.fd.write('24285680:1106497028.38,"(2005, 1, 23, 17, 17, 15, 6, 23, -1)","(2005, 1, 23, 17, 17, 16, 6, 23, -1)",\n')
    
    def testSubject(self):
        tasks = self.writeAndRead()
        self.assertEqual('New task', tasks[0].subject())
        
    def testEffort(self):
        tasks = self.writeAndRead()
        efforts = []
        for task in tasks:
            efforts.extend(task.efforts())
            self.assertEqual(1, len(task.efforts()))
        for effort, description in zip(efforts, ['description', '']):
            self.assertEqual(description, effort.getDescription())
            
    def testTasks(self):
        tasks = self.writeAndRead()
        self.assertEqual(1, len(tasks))
        self.assertEqual(1, len(tasks[0].children()))
            