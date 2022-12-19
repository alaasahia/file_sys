import selectors
import sys
import socket
import types
import psycopg2
import os
from common import load_database
config_path = os.path.join(os.path.expanduser('~'),'.config/file_sys/config')
def load_server():
    return load_database(config_path)


def add_client(ip, cursor):
    cursor.execute(f'insert into devices(ip) values({ip});')


def synchronize(cursor,device, op, names):
    if op == 'add':
        try:
            cursor.execute('select * from devices where device where address={device};')
        except:
            pass
        finally:
            for name in names:
                cursor.execute('insert into table files(name) values("{name}");')
                cursor.execute('insert into table exists(name,address) values("{name}","{address}");')
    else:
        try:
            cursor.execute('delete ')
    
def accept_wrapper(sel,sock):
    conn, addr = sock.accept()
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr,inb=b'', out=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data = data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb = recv_data
        else:
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]
    


db_conn = 


sel = selectors.DefaultSelector()
host = ''
port = 1
lsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsocket.bind((host,port))
lsocket.listen()
lsocket.setblocking(False)
sel.register(lsocket, selectors.EVENT_READ, data = None)
try:
    while True:
        events = sel.select(timeout=0)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print('shutdown server')
finally:
    sel.close()