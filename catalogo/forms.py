from django import forms
from .models import Libro, Autor, Categoria


class LibroForm(forms.ModelForm):

    class Meta:
        model  = Libro
        fields = [
            'titulo', 'autores', 'categoria', 'isbn',
            'editorial', 'anio_publicacion', 'descripcion',
            'ubicacion_fisica', 'cantidad_ejemplares',
            'portada', 'activo'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: El Principito'
            }),
            'autores': forms.SelectMultiple(attrs={
                'class': 'form-select'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 978-3-16-148410-0'
            }),
            'editorial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Alfaguara'
            }),
            'anio_publicacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 2001',
                'min': 1800,
                'max': 2100
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Breve descripción del libro...'
            }),
            'ubicacion_fisica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Estante B - Fila 3'
            }),
            'cantidad_ejemplares': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'portada': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'titulo'             : 'Título',
            'autores'            : 'Autor/es',
            'categoria'          : 'Categoría',
            'isbn'               : 'ISBN',
            'editorial'          : 'Editorial',
            'anio_publicacion'   : 'Año de publicación',
            'descripcion'        : 'Descripción',
            'ubicacion_fisica'   : 'Ubicación física',
            'cantidad_ejemplares': 'Cantidad de ejemplares',
            'portada'            : 'Imagen de portada',
            'activo'             : 'Libro activo en el catálogo',
        }
