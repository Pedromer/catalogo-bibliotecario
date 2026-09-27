from django import forms
from .models import Libro, Autor, Categoria, Etiqueta


class EtiquetaInputField(forms.Field):
    widget = forms.SelectMultiple

    def to_python(self, value):
        if value in self.empty_values:
            return []

        values = value if isinstance(value, (list, tuple)) else [value]
        etiquetas = []
        seen = set()

        for value in values:
            nombre = str(value).strip()

            if not nombre:
                continue

            if len(nombre) > 100:
                raise forms.ValidationError(
                    'Cada etiqueta debe tener como máximo 100 caracteres.'
                )

            normalized = nombre.casefold()
            if normalized not in seen:
                etiquetas.append(nombre)
                seen.add(normalized)

        return etiquetas


class EtiquetasInputMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields.get('etiquetas')
        if field:
            choices = [
                (str(etiqueta.pk), etiqueta.nombre)
                for etiqueta in Etiqueta.objects.order_by('nombre')
            ]
            if self.is_bound:
                field_name = self.add_prefix('etiquetas')
                posted_values = (
                    self.data.getlist(field_name)
                    if hasattr(self.data, 'getlist')
                    else self.data.get(field_name, [])
                )
                if not isinstance(posted_values, (list, tuple)):
                    posted_values = [posted_values]

                known_ids = {value for value, _ in choices}
                choices.extend(
                    (value, value)
                    for value in posted_values
                    if value and value not in known_ids
                )

            field.widget.choices = choices

    def _save_m2m(self):
        nombres = self.cleaned_data.get('etiquetas')

        if nombres is not None:
            etiquetas = []
            seen = set()

            for valor in nombres:
                texto = str(valor).strip()
                etiqueta = None

                if texto.isdecimal():
                    etiqueta = Etiqueta.objects.filter(pk=texto).first()

                if etiqueta is None:
                    etiqueta = Etiqueta.objects.filter(
                        nombre__iexact=texto
                    ).first()

                    if etiqueta is None:
                        etiqueta = Etiqueta.objects.create(nombre=texto)

                if etiqueta.pk not in seen:
                    etiquetas.append(etiqueta)
                    seen.add(etiqueta.pk)

            self.cleaned_data['etiquetas'] = etiquetas

        super()._save_m2m()


class LibroForm(EtiquetasInputMixin, forms.ModelForm):
    etiquetas = EtiquetaInputField(
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select js-etiquetas'}),
        label='Etiquetas',
    )

    class Meta:
        model  = Libro
        fields = [
            'titulo', 'autores', 'categoria', 'isbn',
            'editoriales', 'publicacion', 'coleccion', 'etiquetas', 'descripcion',
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
            'coleccion': forms.Select(attrs={
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
            'coleccion'          : 'Colección',
            'etiquetas'          : 'Etiquetas',
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
