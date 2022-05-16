import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'adfadsf341243#_A'
    MYSQL_DATABASE_URI = os.environ.get('CLEARDB_DATABASE_URL') or 'mysql://root:my_sql123@localhost/lost_and_found'
    MYSQL_USER = os.environ.get('CLEARDB_DATABASE_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('CLEARDB_DATABASE_PASS') or 'my_sql123'
    MYSQL_DB = os.environ.get('CLEARDB_DATABASE_DB') or 'lost_and_found'
