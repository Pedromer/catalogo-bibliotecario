import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 1. Definir o leer la ruta personalizada del admin
ADMIN_URL = os.environ.get('DJANGO_ADMIN_URL', 'gestion-interna/')

# 2. Asegurar que termine con barra inclinada '/'
if not ADMIN_URL.endswith('/'):
    ADMIN_URL += '/'

# 3. Rutas principales (catalogo PRIMERO para que capture sus propias rutas)
urlpatterns = [
    path('', include('catalogo.urls')),
    path(ADMIN_URL, admin.site.urls),
]

# 4. Servir archivos multimedia solo durante desarrollo local
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)