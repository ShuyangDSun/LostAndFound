import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'adfadsf341243#_A'
    MYSQL_DATABASE_URI = os.environ.get('MYSQL_HOST') or 'mysql://root:my_sql123@localhost/lost_and_found'
    DB_USER = os.environ.get('MYSQL_USER') or 'root'
    DB_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'my_sql123'
    DB_NAME = os.environ.get('MYSQL_DB') or 'lost_and_found'
