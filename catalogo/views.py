from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
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
    Soporta búsqueda por texto y filtro por categoría.
    """
    libros     = Libro.objects.filter(activo=True).prefetch_related('autores')
    categorias = Categoria.objects.all().order_by('nombre')

    # Búsqueda por texto
    query = request.GET.get('q', '').strip()
    if query:
        libros = libros.filter(
            Q(titulo__icontains=query) |
            Q(autores__nombre__icontains=query) |
            Q(isbn__icontains=query)
        ).distinct()

    # Filtro por categoría
    categoria_id = request.GET.get('categoria', '')
    if categoria_id:
        libros = libros.filter(categoria__id=categoria_id)

    return render(request, 'catalogo/catalogo_publico.html', {
        'libros'      : libros,
        'categorias'  : categorias,
        'query'       : query,
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
