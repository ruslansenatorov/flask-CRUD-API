import psycopg2
from .config import Config

def getDBConn():
    conn = psycopg2.connect(Config.DATABASE_URL)
    return conn