document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('detalle-imagen-modal');
    const modalImage = document.getElementById('detalle-imagen-modal-img');
    const closeButton = modal?.querySelector('.detalle-imagen-modal-cerrar');
    const imageTriggers = document.querySelectorAll('.detalle-imagen-trigger');

    if (!modal || !modalImage || !closeButton || !imageTriggers.length) return;

    let lastTrigger = null;

    const closeModal = () => {
        modal.hidden = true;
        modalImage.src = '';
        modalImage.alt = '';
        document.body.classList.remove('detalle-modal-abierto');
        lastTrigger?.focus();
    };

    imageTriggers.forEach((trigger) => {
        trigger.addEventListener('click', () => {
            lastTrigger = trigger;
            modalImage.src = trigger.dataset.imagenUrl;
            modalImage.alt = trigger.dataset.imagenAlt;
            modal.hidden = false;
            document.body.classList.add('detalle-modal-abierto');
            closeButton.focus();
        });
    });

    closeButton.addEventListener('click', closeModal);
    modal.addEventListener('click', (event) => {
        if (event.target === modal) closeModal();
    });
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !modal.hidden) closeModal();
    });
});