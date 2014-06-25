from bson.timestamp import Timestamp
from msched import on_event

import pymongo
import sys
import os
import time
import subprocess
import importlib
import inspect
import json

__ACTION_MAP = {}
DEBUG = False

def is_struct_subtype(smalltype, bigtype):
    for k,v in smalltype.iteritems():
        if not(k in bigtype and bigtype[k] == v):
            return False
    return True

def listen_forever(cursor):
    while True:
        for doc in cursor:
            try:
                possible_ops = __ACTION_MAP[doc['op']]
                for p in possible_ops:
                    if is_struct_subtype(p['matcher'], doc['o']):
                        p['responder']()
            except KeyError:
                if DEBUG:
                    print "no ops were registered of type", doc['op']
                continue

if __name__ == '__main__':
    ## Import the scheduler
    import mscheduler

    ## Default mport
    mport = '31337'

    ## See if the user wants to supply a replset
    if len(sys.argv) > 1:
        mport = sys.argv[1]

    else:
        ## Directory plumbing
        if not os.access('/etc/msched', os.F_OK):
            os.mkdir('/etc/msched')

        if not os.access('/etc/msched/data', os.F_OK):
            os.mkdir('/etc/msched/data')

        ## Set up the action map
        __ACTION_MAP = on_event.lookup
        if DEBUG:
            print "actionmap", __ACTION_MAP

        ## Boot up mongod
        try:
            print subprocess.check_output([
                'sudo',
                'mongod',
                '--replSet',
                'msched',
                '--logpath',
                '/etc/msched/msched.log',
                '--dbpath',
                '/etc/msched/data',
                '--port',
                '31337',
                '--fork'
                ])
        except subprocess.CalledProcessError as e:
            if e.returncode == 100:
                print "warn: mongod failed to start with error code 100. continuing"
            else:
                raise e
    ## Access the oplog
    oplog = pymongo.MongoClient('localhost:'+str(mport))['local']['oplog.rs']

    ## Find most recent entry

    ## Set up tailing cursor
    ts = Timestamp(int(time.time()), 1)
    tailer = oplog.find({'ts': { '$gt': ts }},
                        tailable=True,
                        await_data=True,
                        no_cursor_timeout=True)
    
    ## Listen
    listen_forever(tailer)
