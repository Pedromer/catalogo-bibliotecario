"""Migration to rename Autor.nacionalidad -> Autor.pais preserving data."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='autor',
            old_name='nacionalidad',
            new_name='pais',
        ),
    ]
