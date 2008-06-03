
from _pysyncml import *

class BaseSource(SyncSource):
    def __init__(self, objectList, *args, **kwargs):
        super(BaseSource, self).__init__(*args, **kwargs)

        self.objectList = objectList

        self.allObjectsList = [obj for obj in objectList]
        self.newObjectsList = [obj for obj in objectList if obj.isNew()]
        self.changedObjectsList = [obj for obj in objectList if obj.isModified()]

    def _getObject(self, key):
        for obj in self.allObjectsList:
            if obj.id() == key:
                return obj
        raise KeyError, 'No such object: %s' % key

    def _getItem(self, ls):
        try:
            obj = ls.pop(0)
        except IndexError:
            return None, None

        item = SyncItem(obj.id())

        if obj.getStatus() == obj.STATUS_NONE:
            item.state = STATE_NONE
        elif obj.getStatus() == obj.STATUS_NEW:
            item.state = STATE_NEW
        elif obj.getStatus() == obj.STATUS_CHANGED:
            item.state = STATE_UPDATED
        # TODO: deleted...

        return item, obj

    def _parseObject(self, item):
        raise NotImplementedError

    def getFirstItemKey(self):
        return None

    def getNextItemKey(self):
        return None

    def getFirstItem(self):
        self.allObjectsListCopy = self.allObjectsList[:]
        return self._getItem(self.allObjectsListCopy)

    def getNextItem(self):
        return self._getItem(self.allObjectsListCopy)

    def getFirstNewItem(self):
        self.newObjectsListCopy = self.newObjectsList[:]
        return self._getItem(self.newObjectsListCopy)

    def getNextNewItem(self):
        return self._getItem(self.newObjectsListCopy)

    def getFirstUpdatedItem(self):
        self.changedObjectsListCopy = self.changedObjectsList[:]
        return self._getItem(self.changedObjectsListCopy)

    def getNextUpdatedItem(self):
        return self._getItem(self.changedObjectsListCopy)

    def getFirstDeletedItem(self):
        print 'FDI' # TODO

    def getNextDeletedItem(self):
        print 'NDI' # TODO

    def addItem(self, item):
        obj = self._parseObject(item)
        self.objectList.append(obj)
        item.key = obj.id()

        return obj

    def updateItem(self, item):
        obj = self._parseObject(item)

        try:
            local = self._getObject(item.key)
        except KeyError:
            return 404

        return self.doUpdateItem(obj, local)

    def doUpdateItem(self, obj, local):
        raise NotImplementedError

    def deleteItem(self, item):
        try:
            obj = self._getObject(item.key)
        except KeyError:
            return 404

        self.objectList.remove(obj)

        return 200

    def setItemStatus(self, key, status):
        obj = self._getObject(key)

        if status in [200, 201, 418]:
            # 200: Generic OK
            # 201: Added.
            # 418: Already exists.

            obj.cleanDirty()
            return 200

        print 'UNHANDLED ITEM STATUS %s %d' % (key, status)

        return 501
