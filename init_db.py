import os
from database import ensure_database_exists, initialize_database


if __name__ == '__main__':
    ensure_database_exists()
    initialize_database()
    print('Database initialized successfully')
