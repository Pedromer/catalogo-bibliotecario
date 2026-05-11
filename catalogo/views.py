from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Libro
from .forms import LibroForm


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
