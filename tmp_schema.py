import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
for row in cur.execute("PRAGMA table_info('catalogo_libro_editoriales')"):
    print(row)
print('---')
for row in cur.execute("SELECT sql FROM sqlite_master WHERE name='catalogo_libro_editoriales'"):
    print(row)
conn.close()
