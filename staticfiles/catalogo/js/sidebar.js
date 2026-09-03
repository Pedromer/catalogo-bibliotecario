document.addEventListener('DOMContentLoaded', function () {
        const toggle = document.getElementById('toggle-filtros');
        const sidebar = document.getElementById('sidebar-filtros');
        const closeBtn = document.getElementById('close-filtros');
        const layout = document.querySelector('.catalogo-layout');

        if (!toggle || !sidebar) return;

        const isDesktop = () => window.innerWidth >= 992;

        const setSidebarState = (isOpen) => {
            if (isDesktop()) {
                if (layout) {
                    layout.classList.toggle('sidebar-collapsed', !isOpen);
                }
                sidebar.classList.remove('open');
            } else {
                if (layout) {
                    layout.classList.remove('sidebar-collapsed');
                }
                sidebar.classList.toggle('open', isOpen);
            }

            toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        };

        toggle.addEventListener('click', function () {
            const shouldOpen = isDesktop()
                ? layout.classList.contains('sidebar-collapsed')
                : !sidebar.classList.contains('open');
            setSidebarState(shouldOpen);
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                setSidebarState(false);
            });
        }

        window.addEventListener('resize', function () {
            setSidebarState(isDesktop() ? !layout?.classList.contains('sidebar-collapsed') : sidebar.classList.contains('open'));
        });

        // Ajustar el tamaño de fuente de los títulos en los libros sin portada
        const fitMissingCoverTitles = () => {
            document.querySelectorAll('.sin-portada-catalogo span').forEach((title) => {
                let fontSize = 16;
                title.style.fontSize = `${fontSize}px`;

                while (
                    fontSize > 12 &&
                    (title.scrollWidth > title.clientWidth || title.scrollHeight > title.clientHeight)
                ) {
                    fontSize -= 1;
                    title.style.fontSize = `${fontSize}px`;
                }
            });
        };

        fitMissingCoverTitles();
        window.addEventListener('resize', fitMissingCoverTitles);
        //
    });
