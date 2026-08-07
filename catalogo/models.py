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


class Editorial(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Editoriales"

# catalogo/models.py
from cloudinary.models import CloudinaryField

class Libro(models.Model):
    portada = CloudinaryField('Portada', null=True, blank=True)
    contraportada = CloudinaryField('Contraportada', null=True, blank=True)
    titulo              = models.CharField(max_length=300)
    autores             = models.ManyToManyField(Autor)
    categoria           = models.ForeignKey(
                            Categoria, on_delete=models.SET_NULL,
                            null=True, blank=True
                          )
    isbn                = models.CharField(max_length=20, unique=True, blank=True, null=True)
    editoriales         = models.ManyToManyField('Editorial', blank=True)
    anio_publicacion    = models.PositiveIntegerField(null=True, blank=True)
    descripcion         = models.TextField(blank=True)
    ubicacion_fisica    = models.CharField(max_length=100, blank=True)
    cantidad_ejemplares = models.PositiveIntegerField(default=1)
    fecha_ingreso       = models.DateField(auto_now_add=True)
    activo              = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name_plural = "Libros"
        ordering = ['titulo']
