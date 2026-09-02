import os
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Min
from django.core.paginator import Paginator
from .models import Libro, Categoria
from .forms import LibroForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

#########################

def catalogo_publico(request):
    """
    Vista principal del catálogo. Accesible sin login.
    Soporta búsqueda por texto, filtro por categoría y ordenamiento.
    """
    # 1. QuerySets iniciales
    libros = Libro.objects.filter(activo=True).prefetch_related('autores')
    categorias = Categoria.objects.all().order_by('nombre')

    # 2. Obtener todos los parámetros GET
    query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '')
    orden = request.GET.get('orden', 'titulo')

    # 3. Búsqueda por texto
    if query:
        libros = libros.filter(
            Q(titulo__icontains=query) |
            Q(autores__nombre__icontains=query) |
            Q(isbn__icontains=query)
        ).distinct()

    # 4. Filtro por categoría
    if categoria_id:
        libros = libros.filter(categoria__id=categoria_id)

    # 5. Filtro de orden
    if orden in ['titulo', '-titulo', 'anio_publicacion', '-anio_publicacion', 'autor', '-autor']:
        if orden in ['autor', '-autor']:
            # Anotamos el primer autor (alfabéticamente)
            libros = libros.annotate(primer_autor=Min('autores__nombre'))
            if orden == 'autor':
                libros = libros.order_by('primer_autor')
            else:
                libros = libros.order_by('-primer_autor')
        else:
            libros = libros.order_by(orden)

    page_size = request.GET.get('por_pagina', '20')
    if page_size not in ('20', '40'):
        page_size = '20'

    paginator = Paginator(libros, int(page_size))
    page_number = request.GET.get('page')
    libros_pagina = paginator.get_page(page_number)

    pagination_params = request.GET.copy()
    pagination_params.pop('page', None)
    pagination_query = pagination_params.urlencode()

    # 6. Un único return con todo el contexto unificado
    return render(request, 'catalogo/catalogo_publico.html', {
        'libros'      : libros,
        'libros_pagina': libros_pagina,
        'page_size': page_size,
        'pagination_query': pagination_query,
        'categorias'  : categorias,
        'query'       : query,
        'orden'       : orden,
        'categoria_id': categoria_id,
    })

def detalle_libro(request, pk):
    """
    Vista de detalle de un libro. Muestra toda la info,
    portada y contraportada.
    """
    libro = get_object_or_404(Libro, pk=pk, activo=True)
    return render(request, 'catalogo/detalle_libro.html', {'libro': libro})

@login_required                        # Solo bibliotecarios logueados
def agregar_libro(request):
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Libro agregado correctamente.')
            return redirect('catalogo:agregar_libro')
        else:
            messages.error(request, 'Revisá los datos ingresados.')
    else:
        form = LibroForm()

    return render(request, 'catalogo/agregar_libro.html', {'form': form})


@login_required
def editar_libro(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Libro actualizado correctamente.')
            return redirect('catalogo:lista_libros')
    else:
        form = LibroForm(instance=libro)

    return render(request, 'catalogo/agregar_libro.html', {
        'form' : form,
        'libro': libro          # Para saber si es edición en el template
    })


@login_required
def eliminar_libro(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    if request.method == 'POST':
        libro.activo = False    # Baja lógica, no borrado físico
        libro.save()
        messages.success(request, f'"{libro.titulo}" fue dado de baja.')
        return redirect('catalogo:lista_libros')

    return render(request, 'catalogo/confirmar_baja.html', {'libro': libro})

## BUSCAR PORTADA POR ISBN
@login_required
def buscar_portada_isbn(request):
    """
    Consulta ambas fuentes de Open Library:
    1. Covers API directa (-L.jpg en alta calidad).
    2. Endpoint de metadatos (jscmd=data).
    Guarda las encontradas y devuelve una lista de opciones para el modal.
    """
    isbn = request.GET.get('isbn', '').strip().replace('-', '')

    if not isbn:
        return JsonResponse({'encontrado': False, 'error': 'ISBN no proporcionado.'})

    opciones = []

    # -------------------------------------------------------------
    # 1. Opción A: API Covers directa (-L.jpg)
    # -------------------------------------------------------------
    url_covers_api = f'https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false'
    try:
        res_covers = requests.get(url_covers_api, timeout=8, allow_redirects=True)
        if res_covers.status_code == 200 and 'image' in res_covers.headers.get('Content-Type', ''):
            nombre_archivo = f'portadas/portada_isbn_{isbn}_archive.jpg'
            if default_storage.exists(nombre_archivo):
                try:
                    default_storage.delete(nombre_archivo)
                except Exception:
                    pass
            
            ruta_guardada = default_storage.save(nombre_archivo, ContentFile(res_covers.content))
            opciones.append({
                'url_preview': default_storage.url(ruta_guardada),
                'ruta_relativa': ruta_guardada,
                'titulo': 'Edición Digitalizada (Covers API / Archive.org)'
            })
    except Exception:
        pass

    # -------------------------------------------------------------
    # 2. Opción B: Endpoint de metadatos (jscmd=data)
    # -------------------------------------------------------------
    try:
        api_meta_url = f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data'
        res_meta = requests.get(api_meta_url, timeout=8)
        datos_meta = res_meta.json()
        clave = f'ISBN:{isbn}'

        if clave in datos_meta and 'cover' in datos_meta[clave]:
            url_meta = datos_meta[clave]['cover'].get('large') or datos_meta[clave]['cover'].get('medium')
            if url_meta:
                res_img_meta = requests.get(url_meta, timeout=8)
                if res_img_meta.status_code == 200 and 'image' in res_img_meta.headers.get('Content-Type', ''):
                    ext = 'jpg' if 'jpeg' in res_img_meta.headers.get('Content-Type', '') else 'png'
                    nombre_archivo_meta = f'portadas/portada_isbn_{isbn}_edicion.{ext}'
                    
                    if default_storage.exists(nombre_archivo_meta):
                        try:
                            default_storage.delete(nombre_archivo_meta)
                        except Exception:
                            pass

                    ruta_guardada_meta = default_storage.save(nombre_archivo_meta, ContentFile(res_img_meta.content))
                    opciones.append({
                        'url_preview': default_storage.url(ruta_guardada_meta),
                        'ruta_relativa': ruta_guardada_meta,
                        'titulo': 'Portada de Edición (Open Library Books API)'
                    })
    except Exception:
        pass

    if not opciones:
        return JsonResponse({'encontrado': False, 'error': 'No se encontraron portadas en ningún repositorio de Open Library.'})

    return JsonResponse({
        'encontrado': True,
        'opciones': opciones,
        # Mantener fallback por compatibilidad
        'url_preview': opciones[0]['url_preview'],
        'ruta_relativa': opciones[0]['ruta_relativa'],
    })