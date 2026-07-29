import unittest

from config import get_db_connection


class DatabaseFallbackTest(unittest.TestCase):
    def test_returns_a_working_connection(self):
        conn = get_db_connection()
        self.assertIsNotNone(conn)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DATABASE()")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        cursor.close()
        conn.close()


if __name__ == "__main__":
    unittest.main()
