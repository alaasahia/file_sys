import psycopg2
from common import connect_database, create_database
import os
try:
    db_name = 'files'
    conn = connect_database('postgres')
    conn.autocommit(True)
    curs = conn.cursor()
    curs.execute('select datname from pg_database;')
    db_name = create_database(curs, 'files')
    path = os.path.join(os.path.expanduser('~'),'.config/files_sys/')
    os.mkdir(path, 0o776)
    config = open(os.path.join(path,'config', 'w'))
    config.write(f'database={db_name}')
    curs.close()
    conn = connect_database(db_name)
    curs = conn.cursor()
    curs.execute('create table servers(serverId int, ipAddr varchar(15), primary key(serverId));')
    curs.execute('create table files(fileId int primary key, fileName varchar(50)), location varchar(200);')
    curs.execute('create table synchronize(tag bool primary key default true, isSynchronized bool default false);')
    curs.close()
except:
    print('postgres is not running or not installed')