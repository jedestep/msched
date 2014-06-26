from threading import Thread
import time

INITIALIZING = 0
READY = 1
RUNNING = 2
FINISHED = 3

class Worker(Thread):
    def __init__(self, pool):
        Thread.__init__(self)
        self.parent = pool
        self.state = INITIALIZING
        self.fn = None
        self.args = None
        self.parent.available.append(self)

    def prepare(self, fn, args):
        self.fn = fn
        self.args = args
        self.state = READY

    def run(self):
        if self.state == READY:
            self.parent.available.remove(self)
            self.parent.running.append(self)
            self.state = RUNNING
            self.fn(**self.args)
            self.state = FINISHED
            self.release()

    def release(self):
        if self.state == FINISHED:
            self.fn = None
            self.args = None
            self.state = INITIALIZING
            self.parent.running.remove(self)
            self.parent.available.append(self)

class WorkerPool(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WorkerPool, cls).__new__(cls, *args, **kwargs)
            cls._instance.available = []
            cls._instance.running = []
            for i in xrange(8):
                Worker(cls._instance)
        return cls._instance

    def worker_for(self, fn, args):
        worker = self.available[0]
        worker.prepare(fn, args)
        worker.run()
