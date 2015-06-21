from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
import socket
import time

selector = DefaultSelector()
n_jobs = 0

def get(path):
    global n_jobs
    n_jobs += 1
    s = socket.socket()
    s.setblocking(False)
    try:
        s.connect(('emptysqua.re', 80))
    except BlockingIOError:
        pass
    selector.register(s.fileno(), EVENT_WRITE, lambda: connected(s, path))

def connected(s, path):
    selector.unregister(s.fileno())
    s.send(('GET %s HTTP/1.0\r\nHost: emptysqua.re\r\n\r\n' % path).encode())
    buf = []
    selector.register(s.fileno(), EVENT_READ, lambda: readable(s, buf))

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
        callback = key.data
        callback()

print('took %.2f seconds' % (time.time() - start))
