import inspect
import os
from capture import CaptureStdOut, CaptureStdErr
from msched.events import EventRecord
from pymongo import MongoClient
from datetime import datetime

# TODO load the manual event queue from ~/.msched
queue = MongoClient('localhost:31337').msched.userdef

def as_event(capture=None, echo=None):
    def decorator(fn):
        fname = fn.func_name
        pid = os.getpid()
        def interior_crocodile_alligator(*args, **kwargs):
            result = None
            if capture is not None:
                with capture as output:
                    result = fn(*args, **kwargs)
            else:
                result = fn(*args, **kwargs)
            # TODO generalize
            key = 'output'
            if capture:
                key = capture.chan
            queue.insert({
                'caller_pid': pid,
                'fname': fname,
                'time': datetime.now(),
                'result': str(result),
                key: output
            })
            if echo:
                for stream in echo:
                    echo.write('\n'.join(output))
            return result, output
        return interior_crocodile_alligator
    return decorator

def make_event_registrar():
    registry = {}
    def registrar(ev, blocking=False):
        def decorator(fn):
            argspec = inspect.getargspec(fn)
            obj = EventRecord(blocking, fn, argspec)
            obj.update(**ev.get_json())
            ev.register_with(obj, registry)
            return fn
        return decorator
    registrar.lookup = registry
    return registrar

on_event = make_event_registrar()
