import sqlite3
from pathlib import Path

path = Path('smartagri_demo.db')
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("UPDATE users SET email=?, phone=?, password=? WHERE role='admin'", ('adminsmartagri@gmail.com','7842647363','Admin@1722'))
cur.execute("UPDATE users SET password=? WHERE role IN ('farmer','provider','buyer')", ('Vishnu@1722',))
conn.commit()
cur.execute('SELECT id, role, email, phone, password FROM users')
print(cur.fetchall())
conn.close()
