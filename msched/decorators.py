import inspect

def make_event_registrar():
    registry = {}
    def registrar(ev):
        def decorator(fn):
            argspec = inspect.getargspec(fn)
            obj = {
                'matcher': ev.obj,
                'responder': fn,
                'args': argspec.args,
                'varargs': argspec.varargs,
                'keywords': argspec.keywords,
                'defaults': argspec.defaults
            }
            if ev.db:
                obj.update({'db': ev.db})
            if ev.coll:
                obj.update({'coll': ev.coll})
            if hasattr(ev, 'o2'):
                obj.update({'o2': ev.o2})
            if ev.t in registry:
                registry[ev.t].append(obj)
            else:
                registry[ev.t] = [obj]
            return fn
        return decorator
    registrar.lookup = registry
    return registrar

on_event = make_event_registrar()
