class Event(object):
    def __init__(self, obj, db=None, coll=None):
        self.obj = obj
        self.db = db
        self.coll = coll
        self.t = ""

class Insert(Event):
    def __init__(self, obj, db=None, coll=None):
        Event.__init__(self, obj, db, coll)
        self.t = 'i'
