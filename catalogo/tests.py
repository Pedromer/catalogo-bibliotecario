import tablib
from django.test import TestCase
from import_export.results import RowResult

from .models import Autor, Libro
from .resources import LibroResource


class LibroResourceDuplicateImportTests(TestCase):
    def _build_dataset(self, title, authors, isbn='', description=''):
        headers = [
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
            'Contraportada_URL',
        ]
        row = [title, authors, '', isbn, '', '', description, '1', '', '', '']
        return tablib.Dataset(headers=headers, rows=[row])

    def test_duplicate_row_merges_only_new_values(self):
        autor = Autor.objects.create(nombre='Juan Pérez')
        libro_existente = Libro.objects.create(titulo='El libro')
        libro_existente.autores.add(autor)

        resource = LibroResource()
        dataset = self._build_dataset('El libro', 'Juan Pérez', isbn='978-1-23', description='Descripción nueva')

        result = resource.import_data(dataset, raise_errors=True)

        libro_existente.refresh_from_db()
        self.assertEqual(Libro.objects.count(), 1)
        self.assertEqual(libro_existente.isbn, '978-1-23')
        self.assertEqual(libro_existente.descripcion, 'Descripción nueva')
        self.assertEqual(result.totals[RowResult.IMPORT_TYPE_UPDATE], 1)
        self.assertEqual(result.totals[RowResult.IMPORT_TYPE_SKIP], 0)

    def test_duplicate_row_without_new_values_is_skipped(self):
        autor = Autor.objects.create(nombre='Ana García')
        libro_existente = Libro.objects.create(titulo='Otro libro')
        libro_existente.autores.add(autor)

        resource = LibroResource()
        dataset = self._build_dataset('Otro libro', 'Ana García', isbn='', description='')

        result = resource.import_data(dataset, raise_errors=True)

        self.assertEqual(Libro.objects.count(), 1)
        self.assertEqual(result.totals[RowResult.IMPORT_TYPE_UPDATE], 0)
        self.assertEqual(result.totals[RowResult.IMPORT_TYPE_SKIP], 1)
