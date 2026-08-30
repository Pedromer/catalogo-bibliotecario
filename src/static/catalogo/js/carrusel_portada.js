document.addEventListener('DOMContentLoaded', function () {
    // Lógica del carrusel original
    document.querySelectorAll('.libro-card.libro-carousel').forEach(function(card) {
        var images = card.querySelectorAll('.carousel-image');
        if (images.length < 2) return;

        var current = 0;
        var intervalId = null;

        function showIndex(index) {
            images.forEach(function(img, idx) {
                img.classList.toggle('active', idx === index);
            });
        }

        function startCarousel() {
            if (intervalId !== null) return;
            intervalId = setInterval(function() {
                current = (current + 1) % images.length;
                showIndex(current);
            }, 2000);
        }

        function stopCarousel() {
            if (intervalId !== null) {
                clearInterval(intervalId);
                intervalId = null;
            }
            current = 0;
            showIndex(current);
        }

        card.addEventListener('mouseenter', startCarousel);
        card.addEventListener('mouseleave', stopCarousel);
    });
});
