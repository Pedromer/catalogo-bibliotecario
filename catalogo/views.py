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
    Busca portadas estrictamente por ISBN en:
    1. Google Books API.
    2. Open Library Covers API (-L.jpg).
    3. Open Library Metadata API (jscmd=data).
    No almacena archivos en el storage; devuelve solo las URLs para el modal.
    """
    isbn = request.GET.get('isbn', '').strip().replace('-', '')

    if not isbn:
        return JsonResponse({'encontrado': False, 'error': 'ISBN no proporcionado.'})

    opciones = []
    urls_registradas = set()

    # -------------------------------------------------------------
    # 1. GOOGLE BOOKS (Consulta estricta por ISBN)
    # -------------------------------------------------------------
    try:
        url_gb = 'https://www.googleapis.com/books/v1/volumes'
        res_gb = requests.get(url_gb, params={'q': f'isbn:{isbn}'}, timeout=7)
        if res_gb.status_code == 200:
            datos_gb = res_gb.json()
            for item in datos_gb.get('items', []):
                vol = item.get('volumeInfo', {})
                imgs = vol.get('imageLinks', {})

                img_url = (
                    imgs.get('extraLarge') or 
                    imgs.get('large') or 
                    imgs.get('medium') or 
                    imgs.get('thumbnail') or 
                    imgs.get('smallThumbnail')
                )

                if img_url and img_url not in urls_registradas:
                    img_url = img_url.replace('http://', 'https://')
                    if 'zoom=1' in img_url:
                        img_url = img_url.replace('zoom=1', 'zoom=2')

                    urls_registradas.add(img_url)
                    editorial = vol.get('publisher', '')
                    tit = vol.get('title', 'Edición')
                    anio = vol.get('publishedDate', '')[:4] if vol.get('publishedDate') else ''
                    detalles = [d for d in [editorial, anio] if d]
                    etiqueta = f"{tit} ({' - '.join(detalles)})" if detalles else tit

                    opciones.append({
                        'url_preview': img_url,
                        'nombre_archivo': f'portada_gb_{isbn}.jpg',
                        'titulo': f"{etiqueta} [Google Books]"
                    })
                    break
    except Exception:
        pass

    # -------------------------------------------------------------
    # 2. OPEN LIBRARY - Covers API directa (-L.jpg)
    # -------------------------------------------------------------
    url_covers_api = f'https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false'
    try:
        res_covers = requests.head(url_covers_api, timeout=6, allow_redirects=True)
        if res_covers.status_code == 200 and 'image' in res_covers.headers.get('Content-Type', ''):
            if url_covers_api not in urls_registradas:
                urls_registradas.add(url_covers_api)
                opciones.append({
                    'url_preview': url_covers_api,
                    'nombre_archivo': f'portada_isbn_{isbn}_archive.jpg',
                    'titulo': f'ISBN exacto ({isbn}) [Archive.org / Open Library]'
                })
    except Exception:
        pass

    # -------------------------------------------------------------
    # 3. OPEN LIBRARY - Metadatos (jscmd=data)
    # -------------------------------------------------------------
    try:
        api_meta_url = f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data'
        res_meta = requests.get(api_meta_url, timeout=7)
        datos_meta = res_meta.json()
        clave = f'ISBN:{isbn}'

        if clave in datos_meta and 'cover' in datos_meta[clave]:
            url_meta = datos_meta[clave]['cover'].get('large') or datos_meta[clave]['cover'].get('medium')
            if url_meta and url_meta not in urls_registradas:
                urls_registradas.add(url_meta)
                opciones.append({
                    'url_preview': url_meta,
                    'nombre_archivo': f'portada_isbn_{isbn}_edicion.jpg',
                    'titulo': 'Portada de Edición (Open Library API)'
                })
    except Exception:
        pass

    if not opciones:
        return JsonResponse({'encontrado': False, 'error': 'No se encontraron portadas para este ISBN.'})

    return JsonResponse({
        'encontrado': True,
        'opciones': opciones,
        'url_preview': opciones[0]['url_preview'],
        'nombre_archivo': opciones[0]['nombre_archivo']
    })