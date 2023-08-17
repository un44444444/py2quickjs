import concurrent.futures
import json
import threading

import _quickjs


def test():
    return _quickjs.test()


Context = _quickjs.Context
Object = _quickjs.Object
JSException = _quickjs.JSException
StackOverflow = _quickjs.StackOverflow


class Function:
    # There are unit tests demonstrating that we are crashing if different threads are accessing the
    # same runtime, even if it is not at the same time. So we run everything on the same thread in
    # order to prevent this.
    _threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    
    def __init__(self, name, code, *args, **kwargs):
        """
        Arguments:
            name: The name of the function in the provided code that will be executed.
            code: The source code of the function and possibly helper functions, classes, global
                  variables etc.
            own_executor: Create an executor specifically for this function. The default is False in
                          order to save system resources if a large number of functions are created.
        """
        own_executor = False
        if 'own_executor' in kwargs:
            own_executor = kwargs['own_executor']
        if own_executor:
            self._threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._lock = threading.Lock()

        future = self._threadpool.submit(self._compile, name, code)
        concurrent.futures.wait([future])
        self._context, self._f = future.result()

    def __call__(self, *args, **kwargs):
        run_gc = True
        if 'run_gc' in kwargs:
            run_gc = kwargs['run_gc']
        with self._lock:
            future = self._threadpool.submit(self._call, *args, run_gc=run_gc)
            concurrent.futures.wait([future])
            return future.result()

    def set_memory_limit(self, limit):
        with self._lock:
            return self._context.set_memory_limit(limit)

    def set_time_limit(self, limit):
        with self._lock:
            return self._context.set_time_limit(limit)

    def set_max_stack_size(self, limit):
        with self._lock:
            return self._context.set_max_stack_size(limit)

    def memory(self):
        with self._lock:
            return self._context.memory()

    def add_callable(self, global_name, callable):
        with self._lock:
            self._context.add_callable(global_name, callable)

    def gc(self):
        """Manually run the garbage collection.

        It will run by default when calling the function unless otherwise specified.
        """
        with self._lock:
            self._context.gc()

    def execute_pending_job(self):
        with self._lock:
            return self._context.execute_pending_job()

    @property
    def globalThis(self):
        with self._lock:
            return self._context.globalThis

    def _compile(self, name, code):
        context = Context()
        context.eval(code)
        f = context.get(name)
        return context, f

    def _call(self, *args, **kwargs):
        run_gc = True
        if 'run_gc' in kwargs:
            run_gc = kwargs['run_gc']
        def convert_arg(arg):
            if isinstance(arg, (type(None), str, bool, float, int)):
                return arg
            else:
                # More complex objects are passed through JSON.
                return self._context.parse_json(json.dumps(arg))

        try:
            result = self._f(*[convert_arg(a) for a in args])
            if isinstance(result, Object):
                result = json.loads(result.json())            
            return result
        finally:
            if run_gc:
                self._context.gc()
