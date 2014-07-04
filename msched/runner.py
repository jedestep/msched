#!/usr/bin/env python

from bson.timestamp import Timestamp
from msched import on_event, Any

import msched.worker as worker

import pymongo
import json

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
        if not(k in bigtype and (bigtype[k] == v or isinstance(smalltype[k], Any))):
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
            bigtype = 'o'
            if doc['op'] == 'u':
                bigtype = 'o2'
            if is_struct_subtype(p.matcher, doc[bigtype]):
                kwargs = {}
                #resolve db/coll requests
                if p.db or p.coll:
                    target = doc['ns'].split('.')
                    db, coll = target[0], '.'.join(target[1:])
                    if p.db and not p.db == db:
                        continue
                    if p.coll and not p.coll == coll:
                        continue
                #special case: if **doc is an argument, just pass the whole thing
                if p.argspec.keywords and 'doc' in p.argspec.keywords:
                    run_fn(p.responder, doc['o'], p.blocking)
                else:
                    for arg in p.argspec.args:
                        if arg in doc['o'].keys():
                            kwargs.update({arg: doc['o'][arg]})
                    run_fn(p.responder, kwargs, p.blocking)
    except KeyError:
        if DEBUG:
            print "no ops were registered of type", repr(doc['op'])

def listen_forever(cursor):
    while True:
        for doc in cursor:
            process_doc(doc)

if __name__ == '__main__':
    ## Parse arguments
    import argparse
    parser = argparse.ArgumentParser()

    # 'files' argument
    parser.add_argument('--files', '-f', nargs='+', help='one or more source files', default=['mscheduler.py'])

    # 'port' argument
    parser.add_argument('--port', '-p', type=int, default=27017)

    # 'server' argument
    parser.add_argument('--server', 's', default='localhost')

    # 'build-queue' argument
    parser.add_argument('--build-queue', '-b', action='store_true')

    args = parser.parse_args()

    ## Import the scheduler file(s)
    os.chdir(os.getcwd())
    for f in args.files:
        mod_name = f.split('.')[0]
        imp.load_source(mod_name, f)

    if args.build_queue:
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
                str(args.port),
                '--fork'
                ])
        except subprocess.CalledProcessError as e:
            if e.returncode == 100:
                print "warn: mongod failed to start with error code 100. This probably means it was already running."
            else:
                raise e

    ## Set up the action map
    __ACTION_MAP = on_event.lookup
    if DEBUG:
        print "actionmap", __ACTION_MAP

    ## Log the server and port
    if not os.access('~/.msched', os.F_OK):
        os.mkdir('~/.msched')
    logfile = open('~/.msched/msched')
    logfile.write('server=%s\nport=%s' % (server, str(port)))

    ## Access the oplog
    oplog = pymongo.MongoClient(args.server+':'+str(args.port))['local']['oplog.rs']

    ## Set up tailing cursor
    ts = Timestamp(int(time.time()), 1)
    tailer = oplog.find({'ts': { '$gt': ts }},
                        tailable=True,
                        await_data=True,
                        no_cursor_timeout=True)
    
    ## Listen
    listen_forever(tailer)
