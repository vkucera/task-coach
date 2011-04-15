/*
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
*/

#include <Carbon/Carbon.h>

#include "main.h"

static pascal OSStatus handler(EventHandlerCallRef next, EventRef evt, void *obj)
{
    if (GetEventKind(evt) == kEventSystemUserSessionDeactivated)
    {
        PyGILState_STATE gstate;

        gstate = PyGILState_Ensure();

        PyObject *args = Py_BuildValue("");
        PyObject_Call(((PySessionObserver *)obj)->callback, args, NULL);
        Py_DECREF(args);

        PyGILState_Release(gstate);
    }

    return noErr;
}

//==========================================================================
// Init/dealloc

static void pysessionobserver_dealloc(PySessionObserver *self)
{
    if (self->callback)
    {
        // XXXTODO: uninstall handler
        Py_DECREF(self->callback);
    }

    self->ob_type->tp_free((PyObject*)self);
}

static PyObject* pysessionobserver_new(PyTypeObject *type,
                                       PyObject *args,
                                       PyObject *kwargs)
{
    PySessionObserver *self;

    self = (PySessionObserver*)type->tp_alloc(type, 0);

    if (self)
        self->callback = NULL;

    return (PyObject*)self;
}

static int pysessionobserver_init(PySessionObserver *self,
                                  PyObject *args,
                                  PyObject *kwargs)
{
  if (!PyArg_ParseTuple(args, "O:__init__", &self->callback))
        return -1;

     if (self)
     {
         Py_INCREF(self->callback);

         EventTypeSpec tpe[1];
         EventHandlerUPP upp;

         tpe[0].eventClass = kEventClassSystem;
         tpe[0].eventKind = kEventSystemUserSessionDeactivated;

         upp = NewEventHandlerUPP(handler);
         InstallApplicationEventHandler(upp, 1, tpe, NULL, NULL);
     }

     return 0;
}

static PyMethodDef pysessionobserver_methods[] = {
   { NULL }
};

//==========================================================================
// Type object

PyDoc_STRVAR(sessionobserver_doc,
"SessionObserver class");

static PyTypeObject PySessionObserverType = {
   PyObject_HEAD_INIT(NULL)
   0,
   "_sessionmgt.SessionObserver",
   sizeof(PySessionObserver),
   0,
   (destructor)pysessionobserver_dealloc,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
   sessionobserver_doc,
   0,
   0,
   0,
   0,
   0,
   0,
   pysessionobserver_methods,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   (initproc)pysessionobserver_init,
   0,
   pysessionobserver_new,
};

PyTypeObject* PPySessionObserverType = &PySessionObserverType;

static PyMethodDef functions[] = {
    { NULL }
};

void init_sessionmgt(void)
{
    PyObject *mdl = Py_InitModule3("_sessionmgt", functions, "Session management extension");

    if (PyType_Ready(PPySessionObserverType) < 0)
        return;

    Py_INCREF((PyObject *)PPySessionObserverType);
    PyModule_AddObject(mdl, "SessionObserver", (PyObject *)PPySessionObserverType);
}
