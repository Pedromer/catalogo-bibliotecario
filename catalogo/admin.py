from django.contrib import admin
from .models import Libro, Autor, Categoria

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    search_fields = ['nombre']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    pass

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display  = ['titulo', 'categoria', 'anio_publicacion',
                     'cantidad_ejemplares', 'activo']
    list_filter   = ['categoria', 'activo', 'anio_publicacion']
    search_fields = ['titulo', 'autores__nombre', 'isbn']
    filter_horizontal = ['autores']   # selector visual para autores múltiples
