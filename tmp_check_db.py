import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
print([row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")])
print([row for row in cur.execute("SELECT app, name FROM django_migrations ORDER BY id")])
conn.close()
