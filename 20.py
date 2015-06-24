from selectors import DefaultSelector, EVENT_WRITE
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
        s.connect(('localhost', 5000))
    except BlockingIOError:
        pass
    selector.register(s.fileno(), EVENT_WRITE, lambda: connected(s, path))

def connected(s, path):
    global n_jobs
    s.send(('GET %s HTTP/1.0\r\n\r\n' % path).encode())

    buf = []
    while True:
        try:
            chunk = s.recv(1000)
            if not chunk:
                break
            buf.append(chunk)
        except OSError:
            pass

    s.close()
    print((b''.join(buf)).decode().split('\n')[0])
    n_jobs -= 1

start = time.time()
get('/foo')
get('/bar')

while n_jobs:
    events = selector.select()
    for key, mask in events:
        callback = key.data
        callback()

print('took %.2f seconds' % (time.time() - start))
