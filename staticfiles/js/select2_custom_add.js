/* static/js/select2_custom_add.js */

(function () {
    let currentTerm = '';

    // 1. Escuchar la escritura en el input de búsqueda de Select2
    document.addEventListener('input', function (e) {
        if (e.target && e.target.classList.contains('select2-search__field')) {
            currentTerm = e.target.value.trim();
        }
    }, true);

    // 2. Función global para abrir la ventana emergente de Django
    window.__djangoQuickAddPopup = function (event, term) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }

        const cleanTerm = term || currentTerm;

        // Detectar si el campo abierto es 'autores' o 'editoriales'
        let modelName = 'autor';
        let selectName = 'autores';

        const openDropdown = document.querySelector('.select2-container--open');
        if (openDropdown) {
            const prevSelect = openDropdown.previousElementSibling;
            if (prevSelect && prevSelect.tagName === 'SELECT') {
                if (prevSelect.name && prevSelect.name.includes('editorial')) {
                    modelName = 'editorial';
                    selectName = 'editoriales';
                }
            }
        }

        // Construir la URL con los flags nativos de popup de Django
        const popupUrl = `/admin/catalogo/${modelName}/add/?_to_field=id&_popup=1&nombre=${encodeURIComponent(cleanTerm)}`;

        // Buscar el botón nativo "+" si existe para invocar la función oficial del admin
        const addBtn = document.getElementById(`add_id_${selectName}`) || 
                       document.querySelector(`a#add_id_${selectName}`) ||
                       document.querySelector(`a[href*="/admin/catalogo/${modelName}/add/"]`);

        if (addBtn && typeof window.showRelatedObjectPopup === 'function') {
            const tempHref = addBtn.getAttribute('href');
            addBtn.setAttribute('href', popupUrl);
            window.showRelatedObjectPopup(addBtn);
            addBtn.setAttribute('href', tempHref);
        } else {
            // Abrir popup estándar compatible con el script 'popup_response.js' de Django
            const win = window.open(
                popupUrl,
                'related_popup',
                'height=550,width=800,resizable=yes,scrollbars=yes'
            );
            if (win) {
                win.focus();
            } else {
                window.location.href = popupUrl;
            }
        }

        // Cerrar el selector desplegable
        if (window.django && window.django.jQuery) {
            window.django.jQuery('select').select2('close');
        }
    };

    // 3. Inyectar el botón con handlers inline directos (evita que Select2 bloquee el evento)
    function patchSelect2() {
        const messageEl = document.querySelector('.select2-results__message');
        if (messageEl && !messageEl.dataset.patched) {
            const searchField = document.querySelector('.select2-search__field');
            const term = (searchField ? searchField.value.trim() : '') || currentTerm;

            if (term.length > 0) {
                messageEl.dataset.patched = "true";

                // Usamos onclick y onmousedown inline con return false
                messageEl.innerHTML = `
                    <div style="padding: 6px 0; user-select: none;">
                        <span style="color: #64748b; display: block; margin-bottom: 4px; font-size: 13px;">
                            No se encontró "${term}".
                        </span>
                        <button type="button" 
                                onmousedown="window.__djangoQuickAddPopup(event, '${term.replace(/'/g, "\\'")}'); return false;"
                                onclick="window.__djangoQuickAddPopup(event, '${term.replace(/'/g, "\\'")}'); return false;"
                                style="background: none; border: none; padding: 0; color: #10b981; font-weight: 600; text-decoration: underline; cursor: pointer; font-size: 13px; font-family: inherit;">
                            ➕ Añadir nuevo: "${term}"
                        </button>
                    </div>
                `;
            }
        }
    }

    // 4. Observador DOM
    const observer = new MutationObserver(function () {
        patchSelect2();
    });

    document.addEventListener('DOMContentLoaded', function () {
        observer.observe(document.body, { childList: true, subtree: true });
    });
})();