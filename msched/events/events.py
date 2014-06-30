class EventRecord(object):
    def __init__(self, blocking, responder, argspec):
        self.blocking = blocking
        self.responder = responder
        self.argspec = argspec

        self.o2 = None
        self.matcher = {}
        self.db = None
        self.coll = None

        self.is_any = False

    def update(self, **kwargs):
        if 'ANY' in kwargs:
            self.is_any = True
            return
        if 'e1' in kwargs and 'e2' in kwargs:
            self.e1 = kwargs['e1']
            self.e2 = kwargs['e2']
            return
        self.matcher = kwargs['matcher']
        self.db = kwargs.get('db', None)
        self.coll = kwargs.get('coll', None)
        self.o2 = kwargs.get('o2', None)

class Event(object):
    def __init__(self, obj, db=None, coll=None):
        self.obj = obj
        self.db = db
        self.coll = coll
        self.t = ""

    def get_json(self):
        o = {'matcher': self.obj}
        if self.db:
            o.update({'db': self.db})
        if self.coll:
            o.update({'coll': self.coll})
        return o

    def register_with(self, obj, registry):
        if self.t in registry:
            registry[self.t].append(obj)
        else:
            registry[self.t] = [obj]

    def __or__(self, other):
        return ConjunctionEvent(self, other)

class Insert(Event):
    def __init__(self, obj, db=None, coll=None):
        Event.__init__(self, obj, db, coll)
        self.t = 'i'

class Delete(Event):
    def __init__(self, obj, db=None, coll=None):
        Event.__init__(self, obj, db, coll)
        self.t = 'd'

class Update(Event):
    def __init__(self, obj, o2=None, db=None, coll=None):
        Event.__init__(self, obj, db, coll)
        self.o2 = o2
        self.t = 'u'

    def get_json(self):
        o = Event.get_json(self)
        o.update({'o2': self.o2})
        return o

class Any(Event):
    def __init__(self):
        self.t = ['i', 'd', 'u']

    def get_json(self):
        return {'ANY': 'ANY',
                'matcher': {}}

    def register_with(self, obj, registry):
        for t in self.t:
            if t in registry:
                registry[t].append(obj)
            else:
                registry[t] = [obj]

class ConjunctionEvent(Event):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def get_json(self):
        return {
            'e1': self.e1.get_json(),
            'e2': self.e2.get_json()
        }

    def register_with(self, obj, registry):
        # this class is a wrapper and shouldn't be registered
        o1 = EventRecord(obj.blocking, obj.responder, obj.argspec)
        o2 = EventRecord(obj.blocking, obj.responder, obj.argspec)

        o1.update(**self.e1.get_json())
        o2.update(**self.e2.get_json())

        self.e1.register_with(o1, registry)
        self.e2.register_with(o2, registry)
