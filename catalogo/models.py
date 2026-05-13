from django.db import models

class Autor(models.Model):
    nombre = models.CharField(max_length=200)
    pais = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Autores"


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías"


class Libro(models.Model):
    titulo = models.CharField(max_length=300)
    autores = models.ManyToManyField(Autor)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True
    )
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    editorial = models.CharField(max_length=200, blank=True)
    anio_publicacion = models.PositiveIntegerField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    ubicacion_fisica = models.CharField(max_length=100, blank=True,
                                         help_text="Ej: Estante B - Fila 3")
    cantidad_ejemplares = models.PositiveIntegerField(default=1)
    portada = models.ImageField(upload_to='portadas/', blank=True, null=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name_plural = "Libros"
        ordering = ['titulo']
