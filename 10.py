import socket
import time

def get(path):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 5000))
    s.send(('GET %s HTTP/1.0\r\n\r\n' % path).encode())

    buf = []
    while True:
        chunk = s.recv(1000)
        if not chunk:
            break
        buf.append(chunk)

    s.close()
    print((b''.join(buf)).decode().split('\n')[0])

start = time.time()
get('/foo')
get('/bar')
print('took %.2f seconds' % (time.time() - start))
