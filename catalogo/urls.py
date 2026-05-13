from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    # ── Catálogo público (sin login) ──────────────────────────
    path('',                       views.catalogo_publico, name='catalogo_publico'),
    path('libro/<int:pk>/',        views.detalle_libro,    name='detalle_libro'),

    # ── Gestión (solo bibliotecarios) ─────────────────────────
    path('gestion/agregar/',           views.agregar_libro,  name='agregar_libro'),
    path('gestion/editar/<int:pk>/',   views.editar_libro,   name='editar_libro'),
    path('gestion/baja/<int:pk>/',     views.eliminar_libro, name='eliminar_libro'),
]
