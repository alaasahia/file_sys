import socket
import os
from common import connect_database, load_database
import pickle
import selectors
import types
config_path = os.path.join(os.path.expanduser('~'),'.config/file_sys/config')
selector = selectors.DefaultSelector()
db_conn = None
cursor = None
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(())
socket.setblocking(False)
socket.listen()
selector.register(socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data = None)
def load_client():
    db_conn = load_database(config_path)


def add_server(server_ip, cursor):
    try:
        cursor.execute(f'insert into table servers(serverId) values({server_ip});')
        return True
    except:
        return False


def remove_server(server_ip, cursor):
    try:
        cursor.execute(f'delete from table servers where serverId = {server_ip};')
        return True
    except:
        return False


def add_file(file, cursor):
    exists = os.path.exists(file)
    file_name = os.path.basename(file).splitext()[0]
    if exists:
        try:
            cursor.execute(f'insert into table files(name,location) values({file_name},{file});')
            return 1
        except:
            pass


def remove_file(name, cursor):
    try:
        cursor.execute(f'delete from files where name = {name};')
    except:
        pass


def synchronize(cursor,op, names):
    cursor.execute('select * from servers;')
    servers = cursor.fetchall()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for server in servers:
        sock.connect((server, port))
        sock.sendall({
            'type':'synchronize',
            'operation': op,
            'files':names
        })
    sock.close()




def get_local_files(cursor):
    cursor.execute('select * from files order by name;')
    results = cursor.fetchall()
    return results

def get_shared_files(cursor):
    cursor.execute('select * from servers;')
    servers = cursor.fetchall()
    sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    results = []
    for server in servers:
        sock.connect((server,''))
        sock.sendall({
            "type":'fetch',
        })
        recv_data = ''
        while True:
            data = sock.recv(1024)
            if data:
                recv_data += data
        results.extend(pickle.load(recv_data))
    sock.close()
    return results

def accept_connection(sock, selector):
    conn,addr = sock.accpet()
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    selector.register(conn, events, data = data)


#search for a file with a specific name within the database or shared filess, it returns a path for a local file and an ip address for a shared file
def get_file_location(name, cursor):
    cursor.execute(f'select location from files where name = {name};')
    results = cursor.fetchall()
    if results:
        return results[0]
    else:
        cursor.execute('select * from servers;')
        servers = cursor.fetchall()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        addresses = []
        for server in servers:
            socket.connect((server[0],''))
            socket.sendall({
                'type':'search',
                'name':name
            })
            ip = ''
            while True:
                d = socket.recv(1024)
                if d:
                    ips += d
            addresses.append(pickle.load(addresses))




def start_file_retrieve(sock, ip ,name, seek):
    sock.connect((ip,''))
    sock.sendall(
        {
            'type':'get',
            'name':name,
            'seek':seek
        }
    )
#get the shared file    
def get_shared_file(ips:list, name:str, cursor):
    index = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    ip_index = 0
    if len(ips):
        start_file_retrieve()
        data = b''
        file_info = b''
        while True:
            data = sock.recv(1024)
            if data:
                break
            else:
                file_info += data
        file_info = pickle.load(file_info)
        new_file = open('name'+file_info['type'],'w')
        while True:
            data = sock.recv(1024)
            new_file.write(data)
            if data:
                if os.stat(new_file).st_size < file_info['size']:
                    while True:
                        try:
                            ip_index += 1
                            start_file_retrieve(sock, ips[ip_index], name, index)
                        except:
                            pass
                else:
                    break
        cursor.execute('insert into table files(name,location) values({name},{new_file.name});')

        
        
    
                            


def send(selector,key, mask):
    sock = key.fileobj
    data = key.data
    file_data = None
    recv_data = ''
    while True:
        if mask and selectors.EVENT_READ:
            data = sock.recv(1024)
            if data:
                file_data += data
            else:
                break
    file_data = pickle.load(file_data)
    file_location = get_file_location(file_data['name'])
    if file_location:
        target_file = open(file_location, 'r')
        target_file.seek(file_data['position'])
        read = target_file.read(1024)
        while read:
            sock.send(read)
            read = target_file.read(1024)
        sock.close()
        selector.close()
    else:
        pass



def serve_connection(selector):
    while True:
        events = selector.select(timeout = 0)
        for key, mask in events:
            if key.data is None:
                accept_connection()
            else:
                send()




