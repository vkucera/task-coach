import patterns

class Sorter(patterns.ObservableListObserver):
    def postProcessChanges(self):
        self.sort()

class DepthFirstSorter(Sorter):        
    def sort(self):
        self[:] = self.sortDepthFirst(self.original().rootTasks())
        
    def sortDepthFirst(self, tasks):
        result = []
        tasks.sort()
        for task in tasks:
            if task not in self.original():
                continue
            result.append(task)
            children = task.children()[:]
            result.extend(self.sortDepthFirst(children))
        return result
