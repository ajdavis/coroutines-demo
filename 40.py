from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
import socket
import time

selector = DefaultSelector()
n_jobs = 0

class Future:
    def __init__(self):
        self.callback = None

    def resolve(self):
        self.callback()

def get(path):
    global n_jobs
    n_jobs += 1
    s = socket.socket()
    s.setblocking(False)
    try:
        s.connect(('localhost', 5000))
    except BlockingIOError:
        pass

    f = Future()
    f.callback = lambda: connected(s, path)
    selector.register(s.fileno(), EVENT_WRITE, f)

def connected(s, path):
    selector.unregister(s.fileno())
    s.send(('GET %s HTTP/1.0\r\n\r\n' % path).encode())
    buf = []
    f = Future()
    f.callback = lambda: readable(s, buf)
    selector.register(s.fileno(), EVENT_READ, f)

def readable(s, buf):
    global n_jobs
    selector.unregister(s.fileno())
    chunk = s.recv(1000)
    if chunk:
        buf.append(chunk)
        f = Future()
        f.callback = lambda: readable(s, buf)
        selector.register(s.fileno(), EVENT_READ, f)
    else:
        # Finished.
        s.close()
        print((b''.join(buf)).decode().split('\n')[0])
        n_jobs -= 1

start = time.time()
get('/foo')
get('/bar')

while n_jobs:
    events = selector.select()
    for key, mask in events:
        future = key.data
        future.resolve()

print('took %.2f seconds' % (time.time() - start))
