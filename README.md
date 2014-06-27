## msched - Events in MongoDB
Use the MongoDB oplog to schedule operations with Python. 

### Installation
```bash
git clone https://github.com/jedestep/msched
cd msched
sudo python setup.py install
```

### Quick start
All you need to do to use ```msched``` is insert the functions you want to be run in a file called ```mscheduler.py```, and then start the ```msched``` daemon. Here's an example:

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

Now that your scheduler file is ready to go, simply start up the runner:
```bash
$ msched 27017
```

The argument to the runner is a port to be used to connect to your replica set. If you just want to use ```msched``` for message passing and do not have an existing replicated MongoDB instance, omit the port and a single-member replica set will boot up on port 31337.
