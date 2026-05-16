import os, sys
sys.path.insert(0, '/home/pemer/projects/catalogo-bibliotecario')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from catalogo.models import Autor, Categoria, Editorial, Libro

print('Model import OK')
print('Autores count:', Autor.objects.count())
print('Categorias count:', Categoria.objects.count())
print('Editoriales count:', Editorial.objects.count())

author = Autor.objects.first() or Autor.objects.create(nombre='Autor Prueba')
category = Categoria.objects.first() or Categoria.objects.create(nombre='Categoria Prueba')
editorial = Editorial.objects.first() or Editorial.objects.create(nombre='Editorial Prueba')

libro = Libro(titulo='Libro de prueba', categoria=category)
libro.save()
libro.autores.set([author])
libro.editoriales.set([editorial])
libro.save()
print('Libro creado', libro.pk)
print('Autores guardados', [a.nombre for a in libro.autores.all()])
print('Editoriales guardadas', [e.nombre for e in libro.editoriales.all()])
