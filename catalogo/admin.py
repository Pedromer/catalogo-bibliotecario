from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_quill.widgets import QuillWidget
from django_quill.forms import QuillFormField
from unfold.admin import ModelAdmin, TabularInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Libro, Autor, Categoria, Coleccion, Etiqueta, Editorial
from .admin_import_export import LibroImportExportAdmin
from .forms import EtiquetaInputField, EtiquetasInputMixin

from unfold.forms import AdminPasswordChangeForm, UserChangeForm
from unfold.forms import UserCreationForm as UnfoldUserCreationForm


# -- Personalización del Widget --
class FixedQuillWidget(QuillWidget):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        custom_css = """
        <style>
            /* 1. Contenedor principal del widget */
            .django-quill-widget {
                max-width: 100% !important;
                width: 100% !important;
                box-sizing: border-box !important;
                display: block !important;
            }

            /* 2. Caja redimensionable (ql-container) */
            .django-quill-widget .ql-container {
                height: 220px !important;            
                min-height: 150px !important;         
                max-height: 800px !important;         
                resize: vertical !important;          
                overflow-y: auto !important;          
                display: flex !important;
                flex-direction: column !important;
                border-bottom-left-radius: 6px !important;
                border-bottom-right-radius: 6px !important;
            }

            /* 3. Área editable interna (ql-editor) */
            .django-quill-widget .ql-editor {
                flex-grow: 1 !important;
                min-height: 100% !important;
                word-break: break-word !important;
                overflow-wrap: break-word !important;
                white-space: pre-wrap !important;
            }

            /* 4. Fix visual para los menús desplegables */
            .django-quill-widget .ql-snow .ql-picker.ql-header {
                width: 100px !important;
                height: 28px !important;
                font-size: 13px !important;
            }
            .django-quill-widget .ql-snow .ql-picker-label {
                padding: 0 4px !important;
                display: inline-flex !important;
                align-items: center !important;
                font-size: 13px !important;
                line-height: normal !important;
            }
            .django-quill-widget .ql-snow .ql-picker-options {
                background: #ffffff !important;
                border: 1px solid #cbd5e1 !important;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important;
                padding: 4px !important;
                z-index: 9999 !important;
            }
            .django-quill-widget .ql-snow .ql-picker-item {
                font-size: 13px !important;
                line-height: 1.5 !important;
                padding: 4px 8px !important;
                color: #334155 !important;
            }
            .django-quill-widget .ql-snow .ql-picker-item:hover {
                background-color: #f1f5f9 !important;
                color: #2563eb !important;
            }
        </style>
        """
        return mark_safe(html + custom_css)


class EtiquetaAutocompleteSelectMultiple(AutocompleteSelectMultiple):
    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs['data-tags'] = 'true'
        return attrs

    def optgroups(self, name, value, attr=None):
        options = []

        for index, selected_value in enumerate(value or []):
            raw_value = getattr(selected_value, 'pk', selected_value)
            raw_value = str(raw_value)
            etiqueta = (
                Etiqueta.objects.filter(pk=raw_value).first()
                if raw_value.isdecimal()
                else None
            )
            label = etiqueta.nombre if etiqueta else raw_value
            options.append(
                self.create_option(
                    name, raw_value, label, True, index, attrs=attr
                )
            )

        return [(None, options, 0)]


# --- Formulario personalizado para aplicar el widget a 'descripcion' ---
class LibroAdminForm(EtiquetasInputMixin, forms.ModelForm):
    descripcion = QuillFormField(widget=FixedQuillWidget(), required=False)
    etiquetas = EtiquetaInputField(
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select js-etiquetas'}),
        label='Etiquetas',
    )

    class Meta:
        model = Libro
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        autores_widget = self.fields['autores'].widget
        native_widget = getattr(autores_widget, 'widget', autores_widget)
        etiqueta_field = self.fields['etiquetas']
        etiqueta_field.widget = EtiquetaAutocompleteSelectMultiple(
            Libro._meta.get_field('etiquetas'),
            admin.site,
            attrs={'class': native_widget.attrs.get('class', '')},
        )


# --- ModelAdmins ---
@admin.register(Autor)
class AutorAdmin(ModelAdmin):
    list_display = ['nombre', 'pais']
    search_fields = ['nombre']
    ordering = ['nombre']

    # Permite precompletar el nombre desde la URL si se usa el botón + o el enlace de Select2
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        if 'nombre' in request.GET:
            initial['nombre'] = request.GET['nombre']
        return initial


@admin.register(Categoria)
class CategoriaAdmin(ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']
    ordering = ['nombre']

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        if 'nombre' in request.GET:
            initial['nombre'] = request.GET['nombre']
        return initial


@admin.register(Coleccion)
class ColeccionAdmin(ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']
    ordering = ['nombre']

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        if 'nombre' in request.GET:
            initial['nombre'] = request.GET['nombre']
        return initial


@admin.register(Etiqueta)
class EtiquetaAdmin(ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']
    ordering = ['nombre']


@admin.register(Editorial)
class EditorialAdmin(ModelAdmin):
    list_display = ['nombre']
    ordering = ['nombre']
    search_fields = ['nombre']

    # Permite precompletar el nombre desde la URL si se usa el botón + o el enlace de Select2
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        if 'nombre' in request.GET:
            initial['nombre'] = request.GET['nombre']
        return initial


@admin.register(Libro)
class LibroAdmin(LibroImportExportAdmin, ModelAdmin):
    form = LibroAdminForm

    def get_view_on_site_url(self, obj=None):
        if obj is None or not obj.activo:
            return None
        return reverse('catalogo:detalle_libro', args=[obj.pk])

    def save_model(self, request, obj, form, change):
        portada_precargada = request.POST.get('portada_precargada', '').strip()
        
        # Si se seleccionó una portada descargada y el input nativo quedó vacío
        if portada_precargada and not request.FILES.get('portada'):
            obj.portada = portada_precargada

        super().save_model(request, obj, form, change)

    # Columnas visibles en la lista de libros
    list_display = [
        'titulo', 'get_autores', 'categoria', 'coleccion',
        'publicacion', 'cantidad_ejemplares', 'activo'
    ]

    # Filtros en la barra lateral derecha
    list_filter = ['activo']

    # Búsqueda por estos campos
    search_fields = [
        'titulo', 'autores__nombre', 'isbn', 'editoriales__nombre',
        'coleccion__nombre', 'etiquetas__nombre'
    ]

    # Hacer editable el campo activo directo desde la lista
    list_editable = ['activo']

    # Organizar el formulario de carga en secciones
    fieldsets = (
        ('Información principal', {
            'fields': ('titulo', 'autores', 'categoria', 'portada', 'contraportada')
        }),
        ('Detalles de publicación', {
            'fields': (
                'isbn', 'editoriales','coleccion', 'publicacion',
                'etiquetas', 'descripcion'
            )
        }),
        ('Información topográfica y física', {
            'fields': ('topografica', 'ubicacion_fisica', 'cantidad_ejemplares')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )

    # Autocompletado con "chips" para autores y editoriales
    autocomplete_fields = [
        'autores', 'editoriales', 'categoria', 'coleccion', 'etiquetas'
    ]

    # Método auxiliar para mostrar autores en la lista
    def get_autores(self, obj):
        return ", ".join([a.nombre for a in obj.autores.all()])
    get_autores.short_description = 'Autores'

    # --- Carga de Cropper.js y scripts de administración ---
    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.1/cropper.min.css',
                'catalogo/css/buscar_portada.css',
                'catalogo/css/image_cropper.css',
                'catalogo/css/unfold_custom_theme.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.1/cropper.min.js',
            'catalogo/js/image_cropper.js',
            'catalogo/js/select2_custom_add.js',
            'catalogo/js/buscar_portada.js',
        )


# 1. Formulario de Creación extendido
class CustomUserCreationForm(UnfoldUserCreationForm):
    class Meta(UnfoldUserCreationForm.Meta):
        model = User
        # Definimos todos los campos que queremos llenar desde el momento cero.
        # Las contraseñas se manejan solas gracias a UnfoldUserCreationForm.
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


# Desregistrar el User original
admin.site.unregister(User)


# Registrar nuestro UserAdmin personalizado
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    # Formularios de Unfold
    form = UserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm

    # FIELDSETS DE CREACIÓN (add_fieldsets)
    # Heredamos el bloque nativo inicial (que renderiza Usuario y las 2 Contraseñas)
    # y le concatenamos los mismos bloques exactos que tiene la vista de EDICIÓN.
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información personal', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permisos', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
            ),
        }),
    )