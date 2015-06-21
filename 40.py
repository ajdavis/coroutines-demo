from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
import socket
import time

selector = DefaultSelector()
n_jobs = 0

class Future:
    def __init__(self):
        self.callbacks = []

    def resolve(self):
        callbacks = self.callbacks
        self.callbacks = []
        for fn in callbacks:
            fn()

def get(path):
    global n_jobs
    n_jobs += 1
    s = socket.socket()
    s.setblocking(False)
    try:
        s.connect(('emptysqua.re', 80))
    except BlockingIOError:
        pass

    f = Future()
    f.callbacks.append(lambda: connected(s, path))
    selector.register(s.fileno(), EVENT_WRITE, f)

def connected(s, path):
    selector.unregister(s.fileno())
    s.send(('GET %s HTTP/1.0\r\nHost: emptysqua.re\r\n\r\n' % path).encode())
    buf = []
    f = Future()
    f.callbacks.append(lambda: readable(s, buf))
    selector.register(s.fileno(), EVENT_READ, f)

def readable(s, buf):
    global n_jobs
    chunk = s.recv(1000)
    if chunk:
        buf.append(chunk)
    else:
        # Finished.
        selector.unregister(s.fileno())
        s.close()
        print((b''.join(buf)).decode())
        n_jobs -= 1

start = time.time()
get('/blog/')
get('/blog/open-source-bridge/')

while n_jobs:
    events = selector.select()
    for key, mask in events:
        future = key.data
        future.resolve()

print('took %.2f seconds' % (time.time() - start))
