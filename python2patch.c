#include <Python.h>

/*
   每当我需要在 cpython 里面尝试把 一个 PyObject 转换成 const char* 指针时，我会调用这个函数
   const char *s = PyUnicode_AsUTF8(py_object_to_be_converted)
   我们来看看这个函数的定义
*/
const char *PyUnicode_AsUTF8(PyObject *unicode) {
	PyObject *bytes;
	if (PyBytes_Check(unicode)) {  // python2 has bytes already
		bytes = PyObject_Bytes(unicode);
	}
	else {
		bytes = PyUnicodeUCS2_AsUTF8String(unicode);
	}
	//
	const char * result = NULL;
	if (bytes) {
		result = PyBytes_AsString(bytes);
		Py_XDECREF(bytes);
	}
	return result;
}

#if defined(_WIN32) || defined(__CYGWIN__)
    #define Py_IMPORTED_SYMBOL __declspec(dllimport)
    #define Py_EXPORTED_SYMBOL __declspec(dllexport)
    #define Py_LOCAL_SYMBOL
#else
#endif

#       if defined(__cplusplus)
#               define PyMODINIT_FUNC extern "C" Py_EXPORTED_SYMBOL PyObject*
#       else /* __cplusplus */
#               define PyMODINIT_FUNC Py_EXPORTED_SYMBOL PyObject*
#       endif /* __cplusplus */
