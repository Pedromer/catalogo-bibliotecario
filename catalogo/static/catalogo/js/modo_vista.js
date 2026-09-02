document.addEventListener('DOMContentLoaded', function () {

    const btnGrid = document.getElementById('btn-grid');
    const btnList = document.getElementById('btn-list');
    const contenedor = document.getElementById('contenedor-libros');

    // clases de Bootstrap que controlan el grid original
    const gridClasses = ['row-cols-2', 'row-cols-sm-3', 'row-cols-md-4', 'row-cols-lg-5'];

    function setView(viewType) {
        if (!contenedor) return;

        if (viewType === 'list') {
            // Activar Vista Lista
            contenedor.classList.add('vista-lista', 'row-cols-1');
            contenedor.classList.remove(...gridClasses);

            btnList.classList.add('active', 'bg-secondary', 'text-white');
            btnGrid.classList.remove('active', 'bg-secondary', 'text-white');

            localStorage.setItem('catalogoView', 'list');
        } else {
            // Activar Vista Grid (Por defecto)
            contenedor.classList.remove('vista-lista', 'row-cols-1');
            contenedor.classList.add(...gridClasses);

            btnGrid.classList.add('active', 'bg-secondary', 'text-white');
            btnList.classList.remove('active', 'bg-secondary', 'text-white');

            localStorage.setItem('catalogoView', 'grid');
        }
    }

    // Leer la preferencia guardada, si no hay, usar 'grid'
    const savedView = localStorage.getItem('catalogoView') || 'grid';
    setView(savedView);

    // Asignar eventos a los botones
    if (btnGrid && btnList) {
        btnGrid.addEventListener('click', (e) => {
            e.preventDefault();
            setView('grid');
        });
        btnList.addEventListener('click', (e) => {
            e.preventDefault();
            setView('list');
        });
    }


});
