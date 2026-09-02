/* static/js/select2_custom_add.js */

(function () {
    let currentTerm = '';
    let popupOpening = false;

    // 1. Escuchar la escritura en el input de búsqueda de Select2
    document.addEventListener('input', function (e) {
        if (e.target && e.target.classList.contains('select2-search__field')) {
            currentTerm = e.target.value.trim();
        }
    }, true);

    function getOpenSelect() {
        const openDropdown = document.querySelector('.select2-container--open');
        if (!openDropdown) return null;

        const previousElement = openDropdown.previousElementSibling;
        return previousElement && previousElement.tagName === 'SELECT'
            ? previousElement
            : null;
    }

    function isQuickAddField(select) {
        return Boolean(
            select &&
            (select.name.includes('autor') || select.name.includes('editorial'))
        );
    }

    // 2. Función global para abrir la ventana emergente de Django
    window.__djangoQuickAddPopup = function (event, term) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }

        if (popupOpening) return;

        const cleanTerm = term || currentTerm;

        // Detectar si el campo abierto es 'autores' o 'editoriales'
        let modelName = 'autor';
        let selectName = 'autores';

        const activeSelect = getOpenSelect();
        if (!isQuickAddField(activeSelect)) {
            return;
        }

        popupOpening = true;

        if (activeSelect.name.includes('editorial')) {
            modelName = 'editorial';
            selectName = 'editoriales';
        }

        const adminPrefix = window.location.pathname.includes('/catalogo/') 
            ? window.location.pathname.split('/catalogo/')[0] 
            : '';

        // Construir la URL con los flags nativos de popup de Django
        const popupUrl = `${adminPrefix}/catalogo/${modelName}/add/?_to_field=id&_popup=1&nombre=${encodeURIComponent(cleanTerm)}`;
        
        const addBtn = document.getElementById(`add_id_${selectName}`) || 
                       document.querySelector(`a#add_id_${selectName}`) ||
                       document.querySelector(`a[href*="/catalogo/${modelName}/add/"]`);

        if (window.django && window.django.jQuery && activeSelect) {
            window.django.jQuery(activeSelect).select2('close');
        }

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

        currentTerm = '';
        window.setTimeout(function () {
            popupOpening = false;
        }, 500);
    };

    // 3. Inyectar el botón con handlers inline directos (evita que Select2 bloquee el evento)
    function patchSelect2() {
        const activeSelect = getOpenSelect();
        if (!isQuickAddField(activeSelect)) return;

        const messageEl = document.querySelector('.select2-results__message');
        if (messageEl && !messageEl.dataset.patched) {
            const searchField = document.querySelector('.select2-search__field');
            const term = (searchField ? searchField.value.trim() : '') || currentTerm;

            if (term.length > 0) {
                messageEl.dataset.patched = "true";

                // 
                messageEl.innerHTML = `
                    <div style="padding: 6px 0; user-select: none;">
                        <span style="color: #64748b; display: block; margin-bottom: 4px; font-size: 13px;">
                            No se encontró "${term}".
                        </span>
                        <button type="button" 
                                onmousedown="window.__djangoQuickAddPopup(event, '${term.replace(/'/g, "\\'")}'); return false;"
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