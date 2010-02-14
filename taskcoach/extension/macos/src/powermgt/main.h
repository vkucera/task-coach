
#ifndef _MAIN_H_
#define _MAIN_H_

#include <Python.h>

typedef struct
{
      PyObject_HEAD
      io_connect_t rootPort;
      IONotificationPortRef notificationPort;
      CFRunLoopRef runLoop;
} PyPowerObserver;

extern PyTypeObject* PPyPowerObserverType;

#endif /* _MAIN_H_ */
