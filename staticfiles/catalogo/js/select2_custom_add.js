/* static/js/select2_custom_add.js */

document.addEventListener('DOMContentLoaded', function() {
    // Asegurarnos de que el jQuery nativo del admin de Django esté cargado
    if (typeof django !== 'undefined' && django.jQuery) {
        (function($) {
            
            // 1. Modificar el mensaje de "Sin resultados" globalmente
            $.fn.select2.defaults.set('language', $.extend({}, $.fn.select2.defaults.get('language'), {
                noResults: function (params) {
                    var term = params.term || '';
                    if (!term) return "No se encontraron resultados.";
                    
                    // Retornamos el botón inyectado con el término buscado
                    return $(`
                        <span>No se encontró. 
                            <a href="#" class="select2-inline-add-btn" data-term="${term}" style="color: #10b981; font-weight: 600; text-decoration: underline;">
                                ➕ Añadir nuevo: "${term}"
                            </a>
                        </span>
                    `);
                }
            }));

            // Permitir que Select2 renderice nuestro código HTML y no lo tome como texto plano
            $.fn.select2.defaults.set('escapeMarkup', function (markup) {
                return markup;
            });

            // 2. Escuchar el click en nuestro botón inyectado
            // Usamos mousedown para que Select2 no cierre el menú antes de registrar el clic
            $(document).on('mousedown', '.select2-inline-add-btn', function(e) {
                e.preventDefault(); 
                
                var term = $(this).data('term');
                
                // Encontrar cuál es el 'select' original que está abierto actualmente
                var selectElement = $('select').filter(function() { 
                    return $(this).next('.select2-container').hasClass('select2-container--open'); 
                });
                
                var selectId = selectElement.attr('id'); // Ej: "id_autores"
                
                if (selectId) {
                    // Buscar el botón nativo "+" basándonos en el ID del select
                    var addBtn = $('#add_' + selectId); // Ej: "#add_id_autores"
                    
                    if (addBtn.length > 0) {
                        var originalHref = addBtn.attr('href');
                        var separator = originalHref.indexOf('?') !== -1 ? '&' : '?';
                        
                        // Agregar temporalmente el parámetro nombre=termino a la URL del popup
                        var newHref = originalHref + separator + 'nombre=' + encodeURIComponent(term);
                        addBtn.attr('href', newHref);
                        
                        // Hacer un click nativo para invocar el popup oficial de Django
                        addBtn[0].click();
                        
                        // Restaurar la URL original para que no quede pegada en el botón lateral
                        setTimeout(function() {
                            addBtn.attr('href', originalHref);
                        }, 500);
                        
                        // Cerrar el menú desplegable forzadamente
                        selectElement.select2('close');
                    }
                }
            });

        })(django.jQuery);
    }
});