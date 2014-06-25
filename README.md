## msched - Events in MongoDB
```msched``` uses the MongoDB oplog to to turn your day-to-day database operations into event triggers for arbitrary Python code. More than anything, ```msched``` is a simple, no-nonsense extension for any replicated MongoDB instance that is extremely easy and intuitive.

### Using msched
All you need to do to use ```msched``` is insert the functions you want to be run in a file called ```mscheduler.py```, and then start the ```runner``` script. Here's an example:

```python
from msched import on_event, Insert

@on_event(Insert({'_id': 1}))
def foo():
    print "hello world!"
```

Now that your scheduler file is ready to go, simply start up the runner:
``` > sudo python runner.py 27017```

The argument to the runner is a port to be used to connect to your replica set. If you just want to use ```msched``` for message passing and do not have an existing replicated MongoDB instance, omit the port and a single-member replica set will boot up on port 31337.
