import json
import os
import re
import time
from io import BytesIO

import requests
from django.conf import settings
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from PIL import Image

from .models import Autor, Categoria, Editorial, Libro


MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


def _normalize_text(value):
    if value is None:
        return ''

    text = str(value).strip()
    text = re.sub(r'\s+', ' ', text)

    return text


def _normalize_author_name(value):
    """
    Normaliza el nombre de un autor.

    Formato esperado:
        Garcia Marquez, Gabriel

    Si falta el espacio después de la coma:
        Garcia Marquez,Gabriel
    se convierte en:
        Garcia Marquez, Gabriel

    La coma NO se utiliza como separador de autores.
    El separador de autores es ';'.
    """
    if value is None:
        return ''

    text = str(value).strip()

    # Normalizar espacios múltiples
    text = re.sub(r'\s+', ' ', text)

    # Asegurar exactamente un espacio después de la coma.
    text = re.sub(r',\s*', ', ', text)

    return text


def _slugify(value):
    value = _normalize_text(value)
    value = value.lower()
    value = re.sub(r'[^a-z0-9]+', '_', value)
    value = value.strip('_')

    return value or 'imagen'


def _download_image_content(url, filename_prefix, title=None):
    if not url:
        return None

    if isinstance(url, str):
        url = url.strip()

    if not url or not url.lower().startswith(('http://', 'https://')):
        return None

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException:
        return None

    content_length = response.headers.get('Content-Length')

    if content_length:
        try:
            if int(content_length) > MAX_IMAGE_SIZE_BYTES:
                return None
        except (ValueError, TypeError):
            pass

    content = response.content

    if len(content) > MAX_IMAGE_SIZE_BYTES:
        return None

    try:
        image = Image.open(BytesIO(content))
        image.verify()
    except Exception:
        return None

    suffix = os.path.splitext(url.split('?')[0])[1].lower()

    if suffix not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
        suffix = '.jpg'

    safe_title = _slugify(title)
    timestamp = int(time.time() * 1000)

    filename = f"{filename_prefix}_{safe_title}_{timestamp}{suffix}"

    from django.core.files.base import ContentFile

    return ContentFile(content, name=filename)


def _convert_drive_url(url):
    if not url:
        return url

    url_str = str(url).strip()

    if 'drive.google.com' not in url_str:
        return url_str

    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url_str)
    if match:
        return (
            f"https://drive.google.com/uc?"
            f"export=download&id={match.group(1)}"
        )

    match = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', url_str)
    if match:
        return (
            f"https://drive.google.com/uc?"
            f"export=download&id={match.group(1)}"
        )

    return url_str


class GetOrCreateForeignKeyWidget(ForeignKeyWidget):

    def clean(self, value, row=None, **kwargs):
        value = _normalize_text(value)

        if not value:
            return None

        # Usar .filter().first() en vez de get_or_create para evitar MultipleObjectsReturned si hay duplicados
        obj = self.model.objects.filter(
            **{f"{self.field}__iexact": value}
        ).first()

        if not obj:
            obj = self.model.objects.create(
                **{self.field: value}
            )

        return obj


class GetOrCreateManyToManyWidget(ManyToManyWidget):
    """
    Widget para campos ManyToMany.

    IMPORTANTE:
    El separador entre elementos es ';'.
    Esto permite que los nombres puedan contener comas.
    """

    def __init__(
        self,
        *args,
        normalizer=_normalize_text,
        **kwargs
    ):
        kwargs.setdefault('separator', ';')
        self.normalizer = normalizer

        super().__init__(
            *args,
            **kwargs
        )

    def clean(self, value, row=None, **kwargs):
        if not value:
            return self.model.objects.none()

        if isinstance(value, (float, int)):
            ids = [int(value)]
            return self.model.objects.filter(
                pk__in=ids
            )

        values = [
            self.normalizer(item)
            for item in str(value).split(self.separator)
            if self.normalizer(item)
        ]

        if not values:
            return self.model.objects.none()

        instances = []
        seen = set()

        for val in values:
            if val in seen:
                continue

            seen.add(val)

            # Usar .filter().first() en vez de get_or_create para evitar MultipleObjectsReturned
            obj = self.model.objects.filter(
                **{f"{self.field}__iexact": val}
            ).first()

            if not obj:
                obj = self.model.objects.create(
                    **{self.field: val}
                )

            instances.append(obj)

        return self.model.objects.filter(
            pk__in=[obj.pk for obj in instances]
        )


class LibroResource(resources.ModelResource):

    titulo = fields.Field(
        column_name='Titulo',
        attribute='titulo'
    )

    autores = fields.Field(
        column_name='Autores',
        attribute='autores',
        widget=GetOrCreateManyToManyWidget(
            Autor,
            field='nombre',
            normalizer=_normalize_author_name,
        ),
    )

    categoria = fields.Field(
        column_name='Categoria',
        attribute='categoria',
        widget=GetOrCreateForeignKeyWidget(
            Categoria,
            field='nombre',
        ),
    )

    isbn = fields.Field(
        column_name='ISBN',
        attribute='isbn'
    )

    editorial = fields.Field(
        column_name='Editorial',
        attribute='editoriales',
        widget=GetOrCreateManyToManyWidget(
            Editorial,
            field='nombre',
        ),
    )

    publicacion = fields.Field(
        column_name='Publicacion',
        attribute='publicacion'
    )

    descripcion = fields.Field(
        column_name='Descripcion',
        attribute='descripcion'
    )

    cantidad = fields.Field(
        column_name='Cantidad',
        attribute='cantidad_ejemplares',
        default=1
    )

    ubicacion = fields.Field(
        column_name='Ubicacion',
        attribute='ubicacion_fisica'
    )

    portada_url = fields.Field(
        column_name='Portada_URL',
        attribute='portada'
    )

    contraportada_url = fields.Field(
        column_name='Contraportada_URL',
        attribute='contraportada'
    )

    class Meta:
        model = Libro

        import_id_fields = []

        fields = (
            'titulo',
            'autores',
            'categoria',
            'isbn',
            'editorial',
            'publicacion',
            'descripcion',
            'cantidad',
            'ubicacion',
            'portada_url',
            'contraportada_url'
        )

        export_order = (
            'titulo',
            'autores',
            'categoria',
            'isbn',
            'editorial',
            'publicacion',
            'descripcion',
            'cantidad',
            'ubicacion',
            'portada_url',
            'contraportada_url'
        )

        skip_unchanged = False
        report_skipped = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._duplicate_updated = 0
        self._duplicate_skipped = 0
        self._current_row_is_duplicate = False
        self._current_row_has_new_data = False

    def before_import_row(self, row, **kwargs):
        """
        Normaliza campos de texto, convierte enlaces de Drive
        y formatea el texto plano al JSON estructurado de Quill.
        """

        row['Titulo'] = _normalize_text(
            row.get('Titulo')
        )

        row['Autores'] = _normalize_text(
            row.get('Autores')
        )

        row['Categoria'] = _normalize_text(
            row.get('Categoria')
        )

        row['Editorial'] = _normalize_text(
            row.get('Editorial')
        )

        row['Ubicacion'] = _normalize_text(
            row.get('Ubicacion')
        )

        # 1. Procesar Descripción para Quill
        for col_name in [
            'Descripcion',
            'descripcion',
            'DESCRIPCION'
        ]:
            if col_name in row and row[col_name]:
                val = _normalize_text(
                    row[col_name]
                )

                if val:
                    if not (
                        val.startswith('{')
                        and '"html"' in val
                    ):
                        payload = {
                            "html": f"<p>{val}</p>",
                            "delta": json.dumps(
                                {
                                    "ops": [
                                        {
                                            "insert": f"{val}\n"
                                        }
                                    ]
                                }
                            )
                        }
                        row[col_name] = json.dumps(
                            payload
                        )
                    else:
                        row[col_name] = val
                break

        # 2. Convertir enlaces de Google Drive
        row['Portada_URL'] = _convert_drive_url(
            row.get('Portada_URL')
        )

        row['Contraportada_URL'] = _convert_drive_url(
            row.get('Contraportada_URL')
        )

        if not row['Titulo']:
            raise ValueError(
                'Titulo obligatorio'
            )

        if not row['Autores']:
            raise ValueError(
                'Autores obligatorio'
            )

    def _get_author_names(self, row):
        values = row.get('Autores')

        if values is None:
            return []

        if isinstance(values, (list, tuple, set)):
            items = values
        else:
            items = str(values).split(';')

        names = []
        for item in items:
            name = _normalize_author_name(item)
            if name:
                names.append(name)

        return names

    def _find_existing_duplicate(self, row):
        titulo = _normalize_text(
            row.get('Titulo')
        )

        autores = self._get_author_names(
            row
        )

        if not titulo or not autores:
            return None

        queryset = Libro.objects.filter(
            titulo__iexact=titulo
        )

        for autor in autores:
            queryset = queryset.filter(
                autores__nombre__iexact=autor
            )

        return queryset.distinct().first()

    def get_or_init_instance(
        self,
        instance_loader,
        row
    ):
        duplicate = self._find_existing_duplicate(
            row
        )

        if duplicate is not None:
            self._current_row_is_duplicate = True
            self._current_row_has_new_data = False
            return duplicate, False

        self._current_row_is_duplicate = False
        self._current_row_has_new_data = False

        return self.init_instance(row), True

    def _has_value(self, value):
        if value is None:
            return False

        if isinstance(value, str):
            return value.strip() != ''

        return True

    def _merge_duplicate_data(
        self,
        instance,
        row,
        **kwargs
    ):
        changed = False

        isbn_value = _normalize_text(
            row.get('ISBN')
        )

        if (
            self._has_value(isbn_value)
            and not instance.isbn
        ):
            instance.isbn = isbn_value
            changed = True

        if instance.categoria_id is None:
            categoria_value = self.fields[
                'categoria'
            ].clean(
                row,
                **kwargs
            )

            if categoria_value is not None:
                instance.categoria = categoria_value
                changed = True

        autores_value = self.fields[
            'autores'
        ].clean(
            row,
            **kwargs
        )

        if autores_value:
            for autor in autores_value:
                if not instance.autores.filter(
                    pk=autor.pk
                ).exists():
                    instance.autores.add(
                        autor
                    )
                    changed = True

        editorial_value = self.fields[
            'editorial'
        ].clean(
            row,
            **kwargs
        )

        if editorial_value:
            for editorial in editorial_value:
                if not instance.editoriales.filter(
                    pk=editorial.pk
                ).exists():
                    instance.editoriales.add(
                        editorial
                    )
                    changed = True

        if not instance.publicacion:
            publicacion_value = self.fields[
                'publicacion'
            ].clean(
                row,
                **kwargs
            )

            if publicacion_value is not None:
                instance.publicacion = publicacion_value
                changed = True

        descripcion_value = row.get(
            'Descripcion'
        )

        if (
            self._has_value(descripcion_value)
            and not instance.descripcion
        ):
            instance.descripcion = descripcion_value
            changed = True

        cantidad_value = row.get(
            'Cantidad'
        )

        if cantidad_value not in (
            None,
            ''
        ):
            try:
                cantidad_num = int(
                    float(cantidad_value)
                )
            except (
                TypeError,
                ValueError
            ):
                cantidad_num = None

            if (
                cantidad_num is not None
                and cantidad_num > 0
                and instance.cantidad_ejemplares <= 1
            ):
                instance.cantidad_ejemplares = cantidad_num
                changed = True

        ubicacion_value = _normalize_text(
            row.get('Ubicacion')
        )

        if (
            self._has_value(ubicacion_value)
            and not instance.ubicacion_fisica
        ):
            instance.ubicacion_fisica = ubicacion_value
            changed = True

        return changed

    def import_instance(
        self,
        instance,
        row,
        **kwargs
    ):
        if self._current_row_is_duplicate:
            self._current_row_has_new_data = (
                self._merge_duplicate_data(
                    instance,
                    row,
                    **kwargs
                )
            )

            if self._current_row_has_new_data:
                instance.save()

            return

        return super().import_instance(
            instance,
            row,
            **kwargs
        )

    def after_import_row(
        self,
        row,
        row_result,
        **kwargs
    ):
        if self._current_row_is_duplicate:
            if self._current_row_has_new_data:
                self._duplicate_updated += 1
            else:
                self._duplicate_skipped += 1

        super().after_import_row(
            row,
            row_result,
            **kwargs
        )

    def after_import(
        self,
        dataset,
        result,
        **kwargs
    ):
        result.totals[
            'duplicate_updated'
        ] = self._duplicate_updated

        result.totals[
            'duplicate_skipped'
        ] = self._duplicate_skipped

        result.duplicate_report = {
            'updated': self._duplicate_updated,
            'skipped': self._duplicate_skipped,
        }

        return super().after_import(
            dataset,
            result,
            **kwargs
        )

    def skip_row(
        self,
        instance,
        original,
        row,
        import_validation_errors=None
    ):
        cols = [
            'Titulo',
            'Autores',
            'Categoria',
            'ISBN',
            'Editorial',
            'Publicacion',
            'Descripcion',
            'Cantidad',
            'Ubicacion',
            'Portada_URL',
            'Contraportada_URL'
        ]

        any_value = False

        for c in cols:
            v = row.get(c)
            if v is None:
                continue
            if (
                isinstance(v, str)
                and v.strip() == ''
            ):
                continue
            any_value = True
            break

        if not any_value:
            return True

        if (
            self._current_row_is_duplicate
            and not self._current_row_has_new_data
        ):
            return True

        return super().skip_row(
            instance,
            original,
            row,
            import_validation_errors=import_validation_errors
        )

    def import_field(
        self,
        field,
        instance,
        row,
        is_m2m=False,
        **kwargs
    ):
        if (
            not field.attribute
            or field.attribute not in (
                "portada",
                "contraportada"
            )
        ):
            return super().import_field(
                field,
                instance,
                row,
                is_m2m,
                **kwargs
            )

        col = field.column_name

        cleaner = getattr(
            self,
            f"clean_{col.lower()}",
            None
        )

        content = None

        if callable(cleaner):
            content = cleaner(
                row.get(col),
                row=row
            )
        else:
            try:
                content = field.clean(
                    row,
                    **kwargs
                )
            except Exception:
                content = None

        if content:
            name = getattr(
                content,
                'name',
                f"{field.attribute}_{int(time.time()*1000)}.jpg"
            )

            basename = os.path.basename(
                name
            )

            setattr(
                instance,
                f"_tmp_{field.attribute}",
                (basename, content)
            )

        return

    def after_save_instance(
        self,
        instance,
        row,
        **kwargs
    ):
        if kwargs.get('dry_run'):
            return

        saved = False

        for attr in (
            'portada',
            'contraportada'
        ):
            tmp = getattr(
                instance,
                f"_tmp_{attr}",
                None
            )

            if not tmp:
                continue

            name, content = tmp

            try:
                getattr(
                    instance,
                    attr
                ).save(
                    name,
                    content,
                    save=False
                )
                saved = True
            except Exception:
                pass
            finally:
                try:
                    delattr(
                        instance,
                        f"_tmp_{attr}"
                    )
                except Exception:
                    pass

        if saved:
            instance.save()

    def clean_publicacion(
        self,
        value,
        row=None
    ):
        if value in (
            None,
            ''
        ):
            return None

        try:
            year = int(float(value))
        except (
            TypeError,
            ValueError
        ):
            raise ValueError(
                'Publicacion no es un número válido'
            )

        if year < -4000 or year > 2100:
            raise ValueError(
                'Publicacion debe estar entre -4000 y 2100'
            )

        return year

    def clean_cantidad(
        self,
        value,
        row=None
    ):
        if value in (
            None,
            ''
        ):
            return 1

        try:
            cantidad = int(float(value))
        except (
            TypeError,
            ValueError
        ):
            raise ValueError(
                'Cantidad no es un número válido'
            )

        if cantidad < 1:
            raise ValueError(
                'Cantidad debe ser al menos 1'
            )

        return cantidad

    def clean_portada_url(
        self,
        value,
        row=None
    ):
        url = _normalize_text(value)
        if not url:
            return None

        titulo = (
            _normalize_text(row.get('Titulo'))
            if row
            else None
        )

        content = _download_image_content(
            url,
            'portada',
            titulo
        )

        if content is None:
            return None

        return content

    def clean_contraportada_url(
        self,
        value,
        row=None
    ):
        url = _normalize_text(value)
        if not url:
            return None

        titulo = (
            _normalize_text(row.get('Titulo'))
            if row
            else None
        )

        content = _download_image_content(
            url,
            'contraportada',
            titulo
        )

        if content is None:
            return None

        return content

    def dehydrate_autores(self, libro):
        return '; '.join(
            autor.nombre
            for autor in libro.autores.all()
        )

    def dehydrate_categoria(self, libro):
        return (
            libro.categoria.nombre
            if libro.categoria
            else ''
        )

    def dehydrate_editorial(self, libro):
        return '; '.join(
            editorial.nombre
            for editorial in libro.editoriales.all()
        )

    def dehydrate_publicacion(self, libro):
        return libro.publicacion or ''

    def dehydrate_descripcion(self, libro):
        if libro.descripcion:
            return getattr(
                libro.descripcion,
                'plain',
                str(libro.descripcion)
            )

        return ''

    def dehydrate_cantidad(self, libro):
        return libro.cantidad_ejemplares

    def dehydrate_ubicacion(self, libro):
        return libro.ubicacion_fisica or ''

    def _build_absolute_url(
        self,
        relative_url
    ):
        if not relative_url:
            return ''

        request = getattr(
            self,
            'request',
            None
        )

        if request is not None:
            return request.build_absolute_uri(
                relative_url
            )

        site_url = getattr(
            settings,
            'SITE_URL',
            ''
        ).rstrip('/')

        if site_url:
            return f"{site_url}{relative_url}"

        return relative_url

    def dehydrate_portada_url(self, libro):
        if not libro.portada:
            return ''

        return self._build_absolute_url(
            libro.portada.url
        )

    def dehydrate_contraportada_url(self, libro):
        if not libro.contraportada:
            return ''

        return self._build_absolute_url(
            libro.contraportada.url
        )