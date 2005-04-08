import patterns

class Sorter(patterns.ObservableListObserver):
    def postProcessChanges(self):
        self.sort()

class DepthFirstSorter(Sorter):   
    def processChanges(self, *args, **kwargs):
        pass
        
    def sort(self):
        self[:] = self.sortDepthFirst(self.original().rootTasks())
        
    def sortDepthFirst(self, tasks):
        result = []
        tasks.sort()
        for task in tasks:
            result.append(task)
            children = [child for child in task.children() if child in self.original()]
            result.extend(self.sortDepthFirst(children))
        return result
