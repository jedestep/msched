#!/usr/bin/python

from msched import on_event, Insert

@on_event(Insert({'_id': 1.0}, db='test', coll='test'))
def foo():
    print "foo just printed hello!"

@on_event(Insert({'_id': 2.0}))
def bar(a):
    print "I bar'd this value", a
