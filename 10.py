import socket
import time

def get(path):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('emptysqua.re', 80))
    s.send(('GET %s HTTP/1.0\r\nHost: emptysqua.re\r\n\r\n' % path).encode())

    buf = []
    while True:
        chunk = s.recv(1000)
        if not chunk:
            break
        buf.append(chunk)

    s.close()
    print((b''.join(buf)).decode())

start = time.time()
get('/blog/')
get('/blog/open-source-bridge/')
print('took %.2f seconds' % (time.time() - start))
