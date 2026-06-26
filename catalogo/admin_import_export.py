from io import BytesIO

import openpyxl
import tablib
from django.conf import settings

from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX as BaseXLSX
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from .resources import LibroResource


class XLSXPadded(BaseXLSX):
    def create_dataset(self, in_stream):
        xlsx_book = openpyxl.load_workbook(
            BytesIO(in_stream), read_only=True, data_only=True
        )
        dataset = tablib.Dataset()
        sheet = xlsx_book.active
        rows = sheet.iter_rows(values_only=True)

        try:
            headers = list(next(rows))
        except StopIteration:
            return dataset

        dataset.headers = [header if header is not None else '' for header in headers]
        width = len(dataset.headers)
        # Always ignore fully blank rows to avoid importing empty records
        ignore_blanks = True

        for row in rows:
            row_values = list(row)
            if ignore_blanks and not any(value is not None for value in row_values):
                continue

            if width and len(row_values) < width:
                row_values.extend([None] * (width - len(row_values)))
            elif len(row_values) > width:
                extra = len(row_values) - width
                dataset.headers.extend([''] * extra)
                width = len(row_values)
                for i, existing_row in enumerate(dataset._data):
                    dataset._data[i] = tablib.core.Row(
                        list(existing_row) + [None] * extra,
                        tags=getattr(existing_row, 'tags', ()),
                    )

            dataset.append(row_values)

        return dataset


class LibroImportExportAdmin(ImportExportModelAdmin):

    
    resource_class = LibroResource
    formats = [XLSXPadded]
    from_encoding = 'utf-8-sig'
    import_export_change_list_template = 'admin/catalogo/libro/change_list.html'
    import_form_class = ImportForm
    export_form_class = ExportForm
