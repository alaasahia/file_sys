def connect_database(db_name):
    conn = psycopg2.connect(database = db_name, user='postgres', password = 'password', host='127.0.0.1', port=5432)
    conn.autocommit(True)
    return conn

def create_database(cursor, db_name):
    db_name = 'files'
    cursor.execute('select datname from pg_database;')
    db_list = cursor.fetchall()
    if db_name not in db_list:
        i = 0
        while True:
            if db_name + str(i) not in db_list:
                db_name += str(i)
                break
    cursor.execute(f'create database {db_name};')
    return db_name


def load_database(config_path):
    try:
        config = open(config_path, 'r')
        target_line = config.readline().strip
        db_name = target_line[target_line.find('database:'):]
        db_conn = connect_database(db_name)
    except FileNotFoundError:
        db_name = 'files'
        db_name = create_database(db_name)
        conn = connect_database(db_name)
        return conn

def load_config_file(name):
    
        