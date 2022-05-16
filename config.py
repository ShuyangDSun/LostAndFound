import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'adfadsf341243#_A'
    MYSQL_DATABASE_URI = os.environ.get('CLEARDB_DATABASE_URL') or 'mysql://root:my_sql123@localhost/lost_and_found'
    DB_USER = os.environ.get('CLEARDB_DATABASE_USER') or 'root'
    DB_PASSWORD = os.environ.get('CLEARDB_DATABASE_PASS') or 'my_sql123'
    DB_NAME = os.environ.get('CLEARDB_DATABASE_DB') or 'lost_and_found'
