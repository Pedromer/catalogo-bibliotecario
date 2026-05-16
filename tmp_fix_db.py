import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
sql = '''
CREATE TABLE IF NOT EXISTS catalogo_libro_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo VARCHAR(300) NOT NULL,
    isbn VARCHAR(20) NULL UNIQUE,
    anio_publicacion INTEGER NULL,
    descripcion TEXT NOT NULL,
    ubicacion_fisica VARCHAR(100) NOT NULL,
    cantidad_ejemplares INTEGER NOT NULL,
    portada VARCHAR(100) NULL,
    contraportada VARCHAR(100) NULL,
    fecha_ingreso DATE NOT NULL,
    activo BOOL NOT NULL,
    categoria_id BIGINT NULL REFERENCES catalogo_categoria(id) DEFERRABLE INITIALLY DEFERRED
);
INSERT INTO catalogo_libro_new (id, titulo, isbn, anio_publicacion, descripcion, ubicacion_fisica, cantidad_ejemplares, portada, contraportada, fecha_ingreso, activo, categoria_id)
  SELECT id, titulo, isbn, anio_publicacion, descripcion, ubicacion_fisica, cantidad_ejemplares, portada, contraportada, fecha_ingreso, activo, categoria_id
  FROM catalogo_libro;
DROP TABLE catalogo_libro;
ALTER TABLE catalogo_libro_new RENAME TO catalogo_libro;
'''
try:
    cur.executescript(sql)
    conn.commit()
    print('DB schema updated: removed editorial column from catalogo_libro')
except Exception as e:
    print('Error:', e)
finally:
    conn.close()
