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

class Task:
    def __init__(self, coro):
        self.coro = coro
        self.step()

    def step(self):
        try:
            next_future = next(self.coro)
        except StopIteration:
            return

        next_future.callbacks.append(self.step)

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
    selector.register(s.fileno(), EVENT_WRITE, f)
    yield f
    selector.unregister(s.fileno())

    s.send(('GET %s HTTP/1.0\r\nHost: emptysqua.re\r\n\r\n' % path).encode())
    buf = []

    f = Future()
    selector.register(s.fileno(), EVENT_READ, f)

    while True:
        yield f
        chunk = s.recv(1000)
        if chunk:
            buf.append(chunk)
        else:
            break

    # Finished.
    selector.unregister(s.fileno())
    s.close()
    print((b''.join(buf)).decode())
    n_jobs -= 1

start = time.time()
Task(get('/blog/'))
Task(get('/blog/open-source-bridge/'))

while n_jobs:
    events = selector.select()
    for key, mask in events:
        future = key.data
        future.resolve()

print('took %.2f seconds' % (time.time() - start))
