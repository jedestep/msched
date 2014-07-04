## msched - Events in MongoDB
Use the MongoDB oplog to schedule operations with Python. 

### Installation
```bash
git clone https://github.com/jedestep/msched
cd msched
sudo python setup.py install
```

### Quick start
All you need to do to use ```msched``` is decorate the functions you want to run with the ```on_event``` decorator, and then start the ```msched``` worker with the filename as the argument. Here's an example:

```python
from msched import on_event, Insert

@on_event(Insert({'_id': 1}))
def foo():
    print "hello world!"
```
Now, whenever any collection receives an insert where the ```_id``` field is 1, ```foo()``` will be called.

```foo``` doesn't have to be a nullary function. Event handlers can also be set up to process some or all of the information that triggered it.

```python
from msched import on_event, Insert

@on_event(Insert({'_id': 1}))
def foo(a,b):         # the a and b fields of the inserted documents are used as the arguments
    print "foo", a+b  # if the document does not have both a and b as fields, an error is raised

@on_event(Insert({'_id': 2}))
def bar(**doc):       # the special argument name **doc causes the whole document to be passed in 
    print "bar", doc
```

Now that your scheduler file is ready to go, simply start up the worker:
```bash
$ msched -p 27017 -f myfile.py
```

The argument to the worker is a port to be used to connect to your replica set. If you just want to use ```msched``` for message passing and do not have an existing replicated MongoDB instance, add the ```-b``` flag.

### Advanced events
The ```Insert``` events demonstrated above only fire when a document is inserted with the exact key-value pairs defined in its predicate. Obviously there are a lot more behaviors than this which are useful, so several other types of events are available. Here are some examples:

```python
from msched import on_event, Insert, Delete, Any  # Update is coming in the next version!

@on_event(Any())
def f1():
    print 'this fires whenever anything happens; be careful!'

@on_event(Insert({'foo': Any()}))
def f2():
    print 'this fires whenever anything is inserted with a "foo" field'

@on_event(Delete({'bar': 1}))
def f3():
    print 'this fires whenever a document is deleted where "bar" is 1'
    print 'the deleted document will be used to pass in arguments'

@on_event(Insert({'foo': Any()}) | Insert({'bar': Any()}))
def f4():
    print 'this fires when a document with either a foo or a bar field is inserted'
    print 'you can mix insert, delete, and update in conjunctions'
```

### Turning output into events
In some cases (such as using msched alongside [fabric](http://fabfile.org)), it's impractical or unsightly to have database code in your application logic where it's otherwise not used. In this case, you can wrap the outputs of your code (to stdout and stderr) as an event.

```python
import sys
from msched import as_event, CaptureStdOut

@as_event(capture=CaptureStdOut(), echo=sys.stdout)
def foo():
    print 'things that go to stdout will be logged in the msched.userdef collection'
    print 'the function name, timestamp, return value and pid will also be included'
    print 'returned is a pair of the format (<return val>, <output as a list of strs>)'
    return 0
```

_Important note_: the ```as_event``` decorator should ONLY be used for functions that will produce a very low write load. _If you are not already using a replicated MongoDB instance to store data, do not use msched_. Using a database for IPC is a [well-known anti pattern](http://en.wikipedia.org/wiki/Database-as-IPC) and a replicated MongoDB instance is way larger than necessary for simple message passing.
