from api.database import *
import sys
import os

MONGO_SERVER = os.environ.get('MONGO_SERVER', '127.0.0.1').upper()
MONGO_PORT = os.environ.get('MONGO_PORT', '27017').upper()

if __name__ != '__main__':
    try:
        database_handler = DatabaseHandler(f'mongodb://{MONGO_SERVER}:{MONGO_PORT}')
        database_handler.connect_to_db()
    except RuntimeError:
        pass
