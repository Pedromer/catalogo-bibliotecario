from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Libro, Autor, Categoria, Editorial
from .admin_import_export import LibroImportExportAdmin


@admin.register(Autor)
class AutorAdmin(ModelAdmin):
    list_display  = ['nombre', 'pais']
    search_fields = ['nombre']
    ordering      = ['nombre']


@admin.register(Categoria)
class CategoriaAdmin(ModelAdmin):
    list_display  = ['nombre']
    ordering      = ['nombre']


@admin.register(Editorial)
class EditorialAdmin(ModelAdmin):
    list_display = ['nombre']
    ordering = ['nombre']


@admin.register(Libro)
class LibroAdmin(LibroImportExportAdmin, ModelAdmin):

    # Columnas visibles en la lista de libros
    list_display = [
        'titulo', 'get_autores', 'categoria',
        'anio_publicacion', 'cantidad_ejemplares', 'activo'
    ]

    # Filtros en la barra lateral derecha
    list_filter = ['categoria', 'activo', 'anio_publicacion']

    # Búsqueda por estos campos
    search_fields = ['titulo', 'autores__nombre', 'isbn']

    # Hacer editable el campo activo directo desde la lista
    list_editable = ['activo']

    # Organizar el formulario de carga en secciones
    fieldsets = (
        ('Información principal', {
            'fields': ('titulo', 'autores', 'categoria', 'portada', 'contraportada')
        }),
        ('Detalles de publicación', {
            'fields': ('isbn', 'editoriales', 'anio_publicacion', 'descripcion')
        }),
        ('Información física', {
            'fields': ('ubicacion_fisica', 'cantidad_ejemplares')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )

    # Selector visual para autores y editoriales (relaciones ManyToMany)
    filter_horizontal = ['autores', 'editoriales']

    # Método auxiliar para mostrar autores en la lista
    def get_autores(self, obj):
        return ", ".join([a.nombre for a in obj.autores.all()])
    get_autores.short_description = 'Autores'


