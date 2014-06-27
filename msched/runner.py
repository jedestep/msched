#!/usr/bin/env python

from bson.timestamp import Timestamp
from msched import on_event

import msched.worker as worker

import pymongo
import json

import py_compile
import imp
import sys
import os
import time
import subprocess
import inspect

POOL = worker.WorkerPool()
__ACTION_MAP = {}
DEBUG = False
#DEBUG = True

def is_struct_subtype(smalltype, bigtype):
    for k,v in smalltype.iteritems():
        if not(k in bigtype and bigtype[k] == v):
            return False
    return True

def run_fn(fn, args, is_blocking):
    if is_blocking:
        fn(**args)
    else:
        POOL.worker_for(fn, args)

def process_doc(doc):
    try:
        possible_ops = __ACTION_MAP[str(doc['op'])]
        for p in possible_ops:
            smalltype = 'o'
            if doc['op'] == 'u':
                smalltype = 'o2'
            if is_struct_subtype(p['matcher'], doc[smalltype]):
                kwargs = {}
                #resolve db/coll requests
                if 'db' in p or 'coll' in p:
                    target = doc['ns'].split('.')
                    db, coll = target[0], '.'.join(target[1:])
                    if 'db' in p and not p['db'] == db:
                        continue
                    if 'coll' in p and not p['coll'] == coll:
                        continue
                #special case: if **doc is an argument, just pass the whole thing
                if p['keywords'] and 'doc' in p['keywords']:
                    run_fn(p['responder'], doc['o'], p['blocking'])
                else:
                    for arg in p['args']:
                        if arg in doc['o'].keys():
                            kwargs.update({arg: doc['o'][arg]})
                    run_fn(p['responder'], kwargs, p['blocking'])
    except KeyError:
        if DEBUG:
            print "no ops were registered of type", repr(doc['op'])

def listen_forever(cursor):
    while True:
        for doc in cursor:
            process_doc(doc)

if __name__ == '__main__':
    ## Import the scheduler
    try:
        imp.load_source('mscheduler', os.getcwd() + '/mscheduler.py')
    except Exception as e:
        print "No mscheduler.py found in", os.getcwd() + '/mscheduler.py'
        print str(e)
        sys.exit(1)

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

    ## Set up the action map
    __ACTION_MAP = on_event.lookup
    if DEBUG:
        print "actionmap", __ACTION_MAP

    ## Access the oplog
    oplog = pymongo.MongoClient('localhost:'+str(mport))['local']['oplog.rs']

    ## Set up tailing cursor
    ts = Timestamp(int(time.time()), 1)
    tailer = oplog.find({'ts': { '$gt': ts }},
                        tailable=True,
                        await_data=True,
                        no_cursor_timeout=True)
    
    ## Listen
    listen_forever(tailer)
