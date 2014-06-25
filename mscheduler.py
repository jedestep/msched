#!/usr/bin/python

from msched import on_event, Insert

@on_event(Insert({'_id': 1.0}))
def foo():
    print "foo just printed hello!"
