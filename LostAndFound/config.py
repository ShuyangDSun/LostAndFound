import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'adfadsf341243#_A'
    MYSQL_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://root:my_sql123@localhost/lost_and_found'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'my_sql123'
    DB_NAME = os.environ.get('DB_NAME') or 'lost_and_found'
