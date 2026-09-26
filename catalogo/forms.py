from django import forms
from .models import Libro, Autor, Categoria


class LibroForm(forms.ModelForm):

    class Meta:
        model  = Libro
        fields = [
            'titulo', 'autores', 'categoria', 'isbn',
            'editoriales', 'publicacion', 'descripcion',
            'ubicacion_fisica', 'cantidad_ejemplares',
            'portada', 'contraportada', 'activo'
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
            'editoriales': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'placeholder': 'Ej: Alfaguara'
            }),
            'publicacion': forms.NumberInput(attrs={
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
            'topografica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 821.134.2(861)-31"19" G216c 1985'
            }),
            'ubicacion_fisica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Piso 2 - Estante B - Fila 3'
            }),
            'cantidad_ejemplares': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'portada': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),

            'contraportada': forms.ClearableFileInput(attrs={
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
            'editoriales'        : 'Editoriales',
            'publicacion'        : 'Publicación',
            'descripcion'        : 'Descripción',
            'topografica'        : 'Información topográfica',
            'ubicacion_fisica'   : 'Ubicación física',
            'cantidad_ejemplares': 'Cantidad de ejemplares',
            'portada'            : 'Imagen de portada',
            'contraportada'      : 'Imagen de contraportada',
            'activo'             : 'Libro activo en el catálogo',
        }
