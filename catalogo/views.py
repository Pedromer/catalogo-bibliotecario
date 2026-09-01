from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Min
from django.core.paginator import Paginator
from .models import Libro, Categoria
from .forms import LibroForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Libro, Categoria
from .forms import LibroForm


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
