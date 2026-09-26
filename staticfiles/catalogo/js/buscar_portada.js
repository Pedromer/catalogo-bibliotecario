(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        const campoISBN = document.querySelector('input[name$="isbn"]');
        const formulario = document.querySelector('form');

        let inputOculto = document.querySelector('input[name="portada_precargada"]');
        if (!inputOculto && formulario) {
            inputOculto = document.createElement('input');
            inputOculto.type = 'hidden';
            inputOculto.name = 'portada_precargada';
            formulario.appendChild(inputOculto);
        }

        const camposConfig = [
            { nombre: 'portada', tieneLupa: true },
            { nombre: 'contraportada', tieneLupa: false }
        ];

        camposConfig.forEach(({ nombre, tieneLupa }) => {
            const inputArchivo = document.querySelector(`input[name$="${nombre}"]`);
            if (!inputArchivo) return;

            const checkboxClear = document.querySelector(`input[name$="${nombre}-clear"]`);

            let widgetCompleto = inputArchivo.closest('label');
            if (!widgetCompleto || widgetCompleto.parentElement.tagName === 'LABEL') {
                widgetCompleto = inputArchivo.closest('.relative') || inputArchivo.parentElement;
            }

            if (checkboxClear) {
                const contenedorClear = checkboxClear.closest('label') || checkboxClear.closest('.flex') || checkboxClear.parentElement;
                if (contenedorClear && contenedorClear !== widgetCompleto) {
                    contenedorClear.classList.add('django-clear-widget-hidden');
                    contenedorClear.style.border = 'none';
                    contenedorClear.style.background = 'transparent';
                    contenedorClear.style.padding = '0';
                    contenedorClear.style.margin = '0';
                    contenedorClear.style.boxShadow = 'none';
                }
                checkboxClear.style.display = 'none';
                checkboxClear.style.border = 'none';
                checkboxClear.style.background = 'transparent';
            }

            let filaWrapper = widgetCompleto.closest('.buscar-portada-fila-wrapper');
            if (!filaWrapper) {
                filaWrapper = document.createElement('div');
                filaWrapper.className = 'buscar-portada-fila-wrapper';
                widgetCompleto.parentNode.insertBefore(filaWrapper, widgetCompleto);
                filaWrapper.appendChild(widgetCompleto);
            }

            inputArchivo.addEventListener('change', function () {
                if (this.files && this.files.length > 0 && checkboxClear) {
                    checkboxClear.checked = false;
                }
            });

            // Botón de búsqueda (solo en portada)
            if (tieneLupa && !filaWrapper.querySelector('.buscar-portada-btn-lupa')) {
                const botonLupa = document.createElement('button');
                botonLupa.type = 'button';
                botonLupa.title = 'Buscar portada en Open Library';
                botonLupa.className = 'buscar-portada-btn buscar-portada-btn-lupa';
                botonLupa.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                `;
                filaWrapper.appendChild(botonLupa);

                botonLupa.addEventListener('click', function () {
                    const isbn = campoISBN ? campoISBN.value.trim() : '';
                    if (!isbn) {
                        mostrarNotificacion('Ingresá un ISBN antes de buscar.', 'error');
                        return;
                    }

                    botonLupa.innerHTML = `
                        <svg class="buscar-portada-spinner" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" style="opacity:0.25;"></circle>
                            <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" style="opacity:0.75;"></path>
                        </svg>
                    `;
                    botonLupa.disabled = true;

                    const endpointUrl = window.BUSCAR_PORTADA_URL || '/gestion-interna/buscar-portada/';

                    fetch(`${endpointUrl}?isbn=${encodeURIComponent(isbn)}`)
                        .then(r => r.json())
                        .then(datos => {
                            restaurarBotonLupa(botonLupa);

                            if (datos.encontrado === false || (!datos.opciones && !datos.url_preview)) {
                                mostrarNotificacion(datos.error || 'No se pudo encontrar ninguna portada.', 'error');
                                return;
                            }

                            // Leer lista de opciones o fallback singular
                            const opciones = (datos.opciones && datos.opciones.length > 0) 
                                ? datos.opciones 
                                : [{
                                    url_preview: datos.url_preview,
                                    ruta_relativa: datos.ruta_relativa,
                                    titulo: 'Portada encontrada'
                                }];

                            abrirModalPopup(opciones, async function(itemSeleccionado) {
                                try {
                                    if (checkboxClear) checkboxClear.checked = false;
                                    if (inputOculto) inputOculto.value = itemSeleccionado.ruta_relativa;

                                    const res = await fetch(itemSeleccionado.url_preview);
                                    const blob = await res.blob();
                                    const nombreArchivo = itemSeleccionado.ruta_relativa.split('/').pop() || 'portada.jpg';
                                    const archivo = new File([blob], nombreArchivo, { type: blob.type || 'image/jpeg' });

                                    const dt = new DataTransfer();
                                    dt.items.add(archivo);
                                    inputArchivo.files = dt.files;
                                    inputArchivo.dispatchEvent(new Event('change', { bubbles: true }));

                                    actualizarTextoWidget(widgetCompleto, nombreArchivo, false);
                                    habilitarBotonEliminar(filaWrapper, nombre);

                                    mostrarNotificacion('¡Portada cargada! Guardá los cambios.', 'exito');
                                } catch (err) {
                                    mostrarNotificacion('Error al transferir la imagen seleccionada.', 'error');
                                }
                            });
                        })
                        .catch(() => {
                            restaurarBotonLupa(botonLupa);
                            mostrarNotificacion('Error de red al consultar la API.', 'error');
                        });
                });
            }

            // Integración de cropper si existe
            setTimeout(() => {
                const btnCropper = widgetCompleto.parentElement.querySelector('button[title*="recortar" i], .image-cropper-btn');
                if (btnCropper && btnCropper.parentElement !== filaWrapper) {
                    filaWrapper.appendChild(btnCropper);
                }
            }, 50);

            const contenedorDelete = checkboxClear ? (
                checkboxClear.closest('label') ||
                checkboxClear.closest('.flex') ||
                checkboxClear.parentElement ||
                filaWrapper
            ) : filaWrapper;

            // Botón de Eliminar
            if (checkboxClear && !contenedorDelete.querySelector(`.btn-eliminar-${nombre}`)) {
                const btnEliminar = document.createElement('button');
                btnEliminar.type = 'button';
                btnEliminar.title = `Quitar ${nombre}`;
                btnEliminar.className = `buscar-portada-btn btn-eliminar-imagen btn-eliminar-${nombre}`;
                btnEliminar.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                `;

                contenedorDelete.style.display = 'flex';
                contenedorDelete.style.alignItems = 'center';
                contenedorDelete.style.gap = '8px';
                contenedorDelete.style.border = 'none';
                contenedorDelete.style.background = 'transparent';
                contenedorDelete.style.padding = '0';
                contenedorDelete.style.margin = '0';
                contenedorDelete.style.boxShadow = 'none';

                if (checkboxClear && checkboxClear.parentElement === contenedorDelete) {
                    contenedorDelete.insertBefore(btnEliminar, checkboxClear);
                } else {
                    contenedorDelete.insertBefore(btnEliminar, contenedorDelete.firstChild || null);
                }
                btnEliminar.style.display = 'inline-flex';

                btnEliminar.addEventListener('click', function () {
                    if (!confirm(`¿Deseas quitar la ${nombre}? Se eliminará al guardar los cambios.`)) return;

                    checkboxClear.checked = true;
                    inputArchivo.value = '';
                    const dtVacio = new DataTransfer();
                    inputArchivo.files = dtVacio.files;
                    if (inputOculto) inputOculto.value = '';

                    actualizarTextoWidget(widgetCompleto, 'Marcado para eliminar', true);

                    btnEliminar.style.opacity = '0.3';
                    btnEliminar.style.pointerEvents = 'none';
                });
            }
        });

        function actualizarTextoWidget(widget, texto, tachado) {
            const elementos = Array.from(widget.querySelectorAll('*'));
            const textoElem = elementos.find(el => {
                const t = el.textContent.trim();
                return el.children.length === 0 && (
                    t.includes('Choose file') || 
                    t.includes('Seleccionar') || 
                    t.includes('/media/') || 
                    t.includes('Marcado para eliminar') ||
                    t.length > 0
                );
            });

            if (textoElem) {
                textoElem.textContent = texto;
                textoElem.style.textDecoration = tachado ? 'line-through' : 'none';
                textoElem.style.opacity = tachado ? '0.5' : '1';
            }
        }

        function habilitarBotonEliminar(filaWrapper, nombre) {
            const btnEliminar = filaWrapper.querySelector(`.btn-eliminar-${nombre}`);
            if (btnEliminar) {
                btnEliminar.style.opacity = '1';
                btnEliminar.style.pointerEvents = 'auto';
            }
        }

        function restaurarBotonLupa(btn) {
            btn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            `;
            btn.disabled = false;
        }

        function mostrarNotificacion(mensaje, tipo) {
            const existente = document.querySelector('.buscar-portada-toast');
            if (existente) existente.remove();

            const toast = document.createElement('div');
            toast.className = `buscar-portada-toast buscar-portada-toast-${tipo}`;
            toast.textContent = mensaje;

            document.body.appendChild(toast);

            setTimeout(() => toast.classList.add('is-visible'), 10);
            setTimeout(() => {
                toast.classList.remove('is-visible');
                setTimeout(() => toast.remove(), 300);
            }, 4000);
        }

        // Modal Carrusel con soporte de múltiples opciones
        function abrirModalPopup(opciones, onConfirmar) {
            let indiceActual = 0;

            const overlay = document.createElement('div');
            overlay.className = 'buscar-portada-modal-overlay';

            const modal = document.createElement('div');
            modal.className = 'buscar-portada-modal';

            function actualizarContenidoModal() {
                const item = opciones[indiceActual];
                modal.innerHTML = `
                    <div class="buscar-portada-modal-content">
                        <h3 style="margin: 0; font-size: 1rem; font-weight: 600;">¿Querés aplicar esta portada?</h3>
                        <p style="margin: 0; font-size: 0.8rem; opacity: 0.85;">${item.titulo}</p>
                        <div class="buscar-portada-carousel">
                            <button type="button" class="buscar-portada-arrow" id="modal-prev" ${opciones.length <= 1 ? 'disabled style="opacity:0.3;cursor:not-allowed;"' : ''}>❮</button>
                            <img src="${item.url_preview}" alt="Previsualización" class="buscar-portada-preview">
                            <button type="button" class="buscar-portada-arrow" id="modal-next" ${opciones.length <= 1 ? 'disabled style="opacity:0.3;cursor:not-allowed;"' : ''}>❯</button>
                        </div>
                        <div style="font-size: 0.8rem; opacity: 0.7;">Opción ${indiceActual + 1} de ${opciones.length}</div>
                        <div class="buscar-portada-actions">
                            <button type="button" id="modal-confirm" class="buscar-portada-confirm-btn">Usar esta portada</button>
                            <button type="button" id="modal-cancel" class="buscar-portada-cancel-btn">Cancelar</button>
                        </div>
                    </div>
                `;

                modal.querySelector('#modal-prev').addEventListener('click', () => {
                    if (indiceActual > 0) {
                        indiceActual--;
                        actualizarContenidoModal();
                    }
                });

                modal.querySelector('#modal-next').addEventListener('click', () => {
                    if (indiceActual < opciones.length - 1) {
                        indiceActual++;
                        actualizarContenidoModal();
                    }
                });

                modal.querySelector('#modal-confirm').addEventListener('click', () => {
                    onConfirmar(opciones[indiceActual]);
                    document.body.removeChild(overlay);
                });

                modal.querySelector('#modal-cancel').addEventListener('click', () => {
                    document.body.removeChild(overlay);
                });
            }

            actualizarContenidoModal();
            overlay.appendChild(modal);
            document.body.appendChild(overlay);
        }
    });
})();