# catalogo/management/commands/crear_grupos.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalogo.models import Libro, Autor, Categoria, Editorial


class Command(BaseCommand):
    help = 'Crea y sincroniza los grupos "Administrador de biblioteca" y "Auditor".'

    def handle(self, *args, **options):
        modelos = [Libro, Autor, Categoria, Editorial]
        content_types = [ContentType.objects.get_for_model(m) for m in modelos]

        # -------------------------------------------------------------
        # 1. Grupo: Administrador de biblioteca (Acceso total al catálogo)
        # -------------------------------------------------------------
        grupo_admin, _ = Group.objects.get_or_create(name='Administrador de biblioteca')
        permisos_admin = Permission.objects.filter(content_type__in=content_types)
        grupo_admin.permissions.set(permisos_admin)
        self.stdout.write(self.style.SUCCESS('✔ Grupo "Administrador de biblioteca" configurado (CRUD completo).'))

        # -------------------------------------------------------------
        # 2. Grupo: Auditor (Únicamente lectura)
        # -------------------------------------------------------------
        grupo_auditor, _ = Group.objects.get_or_create(name='Auditor')
        
        # Filtramos estrictamente los permisos que comienzan con 'view_'
        permisos_auditor = Permission.objects.filter(
            content_type__in=content_types,
            codename__startswith='view_'
        )
        
        # .set() reemplaza y elimina cualquier permiso previo que no sea de solo lectura
        grupo_auditor.permissions.set(permisos_auditor)
        self.stdout.write(self.style.SUCCESS(f'✔ Grupo "Auditor" configurado con {permisos_auditor.count()} permisos de solo lectura.'))