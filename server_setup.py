import psycopg2
import os
from common import create_database, connect_database

db_name = create_database('files')
db_conn = connect_database(db_name)
cursor = db_conn.cursor()
cursor.execute('create table files(Name varchar(100) primary key);')
cursor.execute('create table devices(address varchar(14) primary key);')
cursor.execute('create table exists(name varchar(100), address varchar(14), primary key(name, address), foreign key(name) references files, foreign key references devices);')
