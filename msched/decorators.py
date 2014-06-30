import inspect
from msched.events import EventRecord

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
