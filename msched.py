import json
class Event(object):
    def __init__(self, obj):
        self.obj = obj
        self.t = ""
    def __str__(self):
        s = {'type': self.t, 'obj': self.obj}
        return json.dumps(s)

class Insert(Event):
    def __init__(self, obj):
        Event.__init__(self, obj)
        self.t = 'i'

def make_event_registrar():
    registry = {}
    def registrar(ev):
        def decorator(fn):
            obj = {
                'matcher': ev.obj,
                'responder': fn
            }
            if ev.t in registry:
                registry[ev.t].append(obj)
            else:
                registry[ev.t] = [obj]
            return fn
        return decorator
    registrar.lookup = registry
    return registrar

on_event = make_event_registrar()