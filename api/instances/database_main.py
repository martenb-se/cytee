from api.database import *
import sys

if __name__ != '__main__':
    try:
        database_handler = DatabaseHandler('mongodb://127.0.0.1:27017')
        if hasattr(sys, '_called_from_test'):
            database_handler.connect_to_db()
    except RuntimeError:
        pass
