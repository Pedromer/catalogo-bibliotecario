import re
import json
from django.db import models
from django_quill.fields import QuillField
from django_quill.quill import Quill

class Autor(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    pais = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Autores"


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías"


class Editorial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Editoriales"


class Libro(models.Model):
    portada = models.FileField(upload_to='portadas/', null=True, blank=True)
    contraportada = models.FileField(upload_to='contraportadas/', null=True, blank=True)
    titulo = models.CharField(max_length=300)
    autores = models.ManyToManyField(Autor)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    editoriales = models.ManyToManyField('Editorial', blank=True)
    publicacion = models.IntegerField(null=True, blank=True)
    descripcion = QuillField(blank=True, null=True)
    topografica = models.CharField(max_length=100, blank=True)
    ubicacion_fisica = models.CharField(max_length=100, blank=True)
    cantidad_ejemplares = models.PositiveIntegerField(default=1)
    fecha_ingreso = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.descripcion:
            try:
                # 1. Si es un objeto de django-quill
                if hasattr(self.descripcion, 'html') and hasattr(self.descripcion, 'delta'):
                    html_actual = str(self.descripcion.html or '')
                    delta_actual = self.descripcion.delta

                    # Si hubo cambios en las URLs, reasignamos el objeto Quill completo
                    if html_normalizado != html_actual or delta_normalizado != str(delta_actual):
                        payload = {
                            "html": html_normalizado,
                            "delta": delta_normalizado
                        }
                        self.descripcion = Quill(json.dumps(payload))

                # 2. Si viene como string plano o JSON serializado (ej: importador de Excel)
                elif isinstance(self.descripcion, str):
                    texto_limpio = self.descripcion.strip()
                    if texto_limpio.startswith('{') and '"html"' in texto_limpio:
                        try:
                            data = json.loads(texto_limpio)
                            if 'html' in data:
                                data['html'] = normalizar_urls_youtube(data['html'])
                            if 'delta' in data:
                                data['delta'] = normalizar_urls_youtube(str(data['delta']))
                            self.descripcion = Quill(json.dumps(data))
                        except Exception:
                            self.descripcion = Quill(texto_limpio)
                    else:
                        texto_con_urls = normalizar_urls_youtube(texto_limpio)
                        payload = {
                            "html": f"<p>{texto_con_urls}</p>",
                            "delta": json.dumps({"ops": [{"insert": f"{texto_con_urls}\n"}]})
                        }
                        self.descripcion = Quill(json.dumps(payload))

            except Exception as e:
                print(f"Error procesando Quill: {e}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name_plural = "Libros"
        ordering = ['titulo']