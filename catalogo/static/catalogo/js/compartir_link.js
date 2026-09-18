

document.addEventListener('DOMContentLoaded', () => {
    const tituloLibro = "{{ libro.titulo|escapejs }}";
    const urlActual = window.location.href;
    const textoCompartir = `Mirá este libro en la Biblioteca ESET-UNQ: "${tituloLibro}"`;

    // 1. Enlace para WhatsApp
    // Al compartir solo la URL, WhatsApp detecta el link inmediatamente para generar la tarjeta
    const btnWhatsapp = document.getElementById('share-whatsapp');
    btnWhatsapp.href = `https://api.whatsapp.com/send?text=${encodeURIComponent(urlActual)}`;
    
    // 2. Enlace para Twitter / X
    const btnTwitter = document.getElementById('share-twitter');
    btnTwitter.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(textoCompartir)}&url=${encodeURIComponent(urlActual)}`;

    // 3. Botón de Copiar Enlace
    const btnCopiar = document.getElementById('btn-copiar-enlace');
    const feedback = document.getElementById('copiado-feedback');
    btnCopiar.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(urlActual);
            feedback.style.display = 'block';
            setTimeout(() => {
                feedback.style.display = 'none';
            }, 3000);
        } catch (err) {
            // Alternativa para navegadores que bloqueen clipboard
            const tempInput = document.createElement('input');
            tempInput.value = urlActual;
            document.body.appendChild(tempInput);
            tempInput.select();
            document.execCommand('copy');
            document.body.removeChild(tempInput);
            feedback.style.display = 'block';
            setTimeout(() => {
                feedback.style.display = 'none';
            }, 3000);
        }
    });

    // 4. Web Share API nativa (se activa en Android/iOS o navegadores que la soporten)
    const btnNative = document.getElementById('btn-share-native');
    if (navigator.share) {
        btnNative.style.display = 'inline-block';
        btnNative.addEventListener('click', async () => {
            try {
                await navigator.share({
                    title: tituloLibro,
                    text: textoCompartir,
                    url: urlActual
                });
            } catch (err) {
                if (err.name !== 'AbortError') {
                    console.warn('Error al compartir:', err);
                }
            }
        });
    }
});