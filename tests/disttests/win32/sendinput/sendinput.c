
#include <windows.h>
#include <Python.h>

/* win32all does not seem to include a binding for SendInput, so do it
   by hand. */

static PyObject* PySendInput(PyObject *self, PyObject *args)
{
    INPUT *pInputs;
    int i;

    pInputs = (INPUT*)malloc(sizeof(INPUT) * PyTuple_Size(args));

    ZeroMemory(pInputs, sizeof(INPUT) * PyTuple_Size(args));

    for (i = 0; i < PyTuple_Size(args); ++i)
    {
        PyObject *type;
        PyObject *tpl = PyTuple_GetItem(args, i);

        if (!PyTuple_Check(tpl))
        {
            PyErr_SetString(PyExc_TypeError, "Arguments must be tuples.");
            goto err;
        }

        if (PyTuple_Size(tpl) != 2)
        {
            PyErr_SetString(PyExc_TypeError, "Arguments must be 2-tuples.");
            goto err;
        }

        type = PyTuple_GetItem(tpl, 0);
        if (!PyInt_Check(type))
        {
            PyErr_SetString(PyExc_TypeError, "Struct type must be int.");
            goto err;
        }

        switch (PyInt_AsLong(type))
        {
        case INPUT_MOUSE:
        {
            int dx, dy, mouseData, flags, time;
            PyObject *minput;

            minput = PyTuple_GetItem(tpl, 1);

            if (!PyTuple_Check(minput))
            {
                PyErr_SetString(PyExc_TypeError, "Structure must be a tuple");
                goto err;
            }

            if (!PyArg_ParseTuple(minput, "iiiii", &dx, &dy, &mouseData, &flags, &time))
                goto err;

            pInputs[i].type = INPUT_MOUSE;
            pInputs[i].mi.dx = dx;
            pInputs[i].mi.dy = dy;
            pInputs[i].mi.mouseData = mouseData;
            pInputs[i].mi.dwFlags = flags;
            pInputs[i].mi.time = time;

            break;
        }

        case INPUT_KEYBOARD:
        {
            PyErr_SetString(PyExc_NotImplementedError, "Not implemented");
            goto err;
        }

        default:
            PyErr_SetString(PyExc_ValueError, "Unknown input type.");
            goto err;
        }
    }

    if (SendInput(PyTuple_Size(args), pInputs, sizeof(INPUT)) != PyTuple_Size(args))
    {
        PyErr_SetString(PyExc_RuntimeError, "SendInput failed.");
        goto err;
    }

    free(pInputs);

    Py_INCREF(Py_None);
    return Py_None;

err:
    free(pInputs);

    return NULL;
}

static PyMethodDef functions[] = {
    { "SendInput", (PyCFunction)PySendInput, METH_VARARGS, "SendInput wrapper" },

    { NULL }
};

__declspec(dllexport) void initsendinput(void)
{
    PyObject *mdl;

    if (!(mdl = Py_InitModule3("sendinput", functions, "SendInput module")))
        return;

#define ADDCST(name) PyModule_AddIntConstant(mdl, #name, name)

    ADDCST(INPUT_MOUSE);
    ADDCST(INPUT_KEYBOARD);
    ADDCST(MOUSEEVENTF_ABSOLUTE);
    ADDCST(MOUSEEVENTF_MOVE);
    ADDCST(MOUSEEVENTF_LEFTDOWN);
    ADDCST(MOUSEEVENTF_LEFTUP);
    ADDCST(MOUSEEVENTF_RIGHTDOWN);
    ADDCST(MOUSEEVENTF_RIGHTUP);
    ADDCST(MOUSEEVENTF_MIDDLEDOWN);
    ADDCST(MOUSEEVENTF_MIDDLEUP);
    //ADDCST(MOUSEEVENTF_VIRTUALDESK);
    ADDCST(MOUSEEVENTF_WHEEL);
    ADDCST(MOUSEEVENTF_XDOWN);
    ADDCST(MOUSEEVENTF_XUP);
}
