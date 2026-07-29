from database import initialize_database as _initialize_database

ROLE_PREFIX = {"farmer": "FAR", "provider": "PRO", "buyer": "BUY"}


def initialize_database(connection):
    return _initialize_database(connection)


def generate_user_id(role, connection):
    prefix = ROLE_PREFIX.get(role, "USR")
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM users")
    row = cursor.fetchone()
    total = row[0] if row else 0
    cursor.close()
    return f"{prefix}{int(total) + 1:04d}"
