/* static/js/image_cropper.js */

(function () {
    let cropper = null;
    let activeInput = null;
    let activeFileName = 'imagen_recortada.jpg';
    let modalPromise = null;

    function ensureModalExists() {
        if (document.getElementById('cropper-modal')) {
            return Promise.resolve();
        }

        if (!modalPromise) {
            modalPromise = fetch('/static/catalogo/html/image_cropper.html')
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error('No se pudo cargar el modal del cropper.');
                    }
                    return response.text();
                })
                .then(function (html) {
                    document.body.insertAdjacentHTML('beforeend', html);

                    const modal = document.getElementById('cropper-modal');
                    if (!modal) return;

                    const cancelBtn = document.getElementById('cancel-crop-btn');
                    const closeBtn = document.getElementById('close-cropper-x');
                    const applyBtn = document.getElementById('apply-crop-btn');

                    if (cancelBtn) cancelBtn.onclick = closeCropperModal;
                    if (closeBtn) closeBtn.onclick = closeCropperModal;

                    const ratioBtns = modal.querySelectorAll('.unfold-crop-ratio-btn');
                    ratioBtns.forEach(function (btn) {
                        btn.onclick = function () {
                            ratioBtns.forEach(function (item) {
                                item.classList.remove('active');
                            });
                            this.classList.add('active');

                            const ratio = parseFloat(this.dataset.ratio);
                            if (cropper) {
                                cropper.setAspectRatio(Number.isNaN(ratio) ? NaN : ratio);
                            }
                        };
                    });

                    if (applyBtn) {
                        applyBtn.onclick = function () {
                            if (!cropper || !activeInput) return;

                            const canvas = cropper.getCroppedCanvas({
                                imageSmoothingEnabled: true,
                                imageSmoothingQuality: 'high'
                            });

                            canvas.toBlob(function (blob) {
                                if (!blob) return;

                                const cleanName = (activeFileName || 'imagen.jpg').replace(/\.[^/.]+$/, '') + '.jpg';
                                const croppedFile = new File([blob], cleanName, {
                                    type: 'image/jpeg',
                                    lastModified: Date.now()
                                });
                                croppedFile.isCropped = true;

                                const dataTransfer = new DataTransfer();
                                dataTransfer.items.add(croppedFile);
                                activeInput.files = dataTransfer.files;

                                if (activeInput._cropBtn) {
                                    activeInput._cropBtn.dataset.imgSrc = canvas.toDataURL('image/jpeg');
                                    activeInput._cropBtn.style.display = 'inline-flex';
                                }

                                closeCropperModal();
                            }, 'image/jpeg', 0.92);
                        };
                    }
                })
                .catch(function (error) {
                    console.error(error);
                });
        }

        return modalPromise;
    }

    function openCropperModal(fieldName, imgSrc, fileName, inputElem) {
        activeInput = inputElem;
        activeFileName = fileName || 'portada.jpg';

        ensureModalExists().then(function () {
            const modal = document.getElementById('cropper-modal');
            const img = document.getElementById('image-to-crop');
            const title = document.getElementById('cropper-modal-title');

            if (!modal || !img || !title) return;

            title.textContent = 'Ajustar / Recortar ' + fieldName.toUpperCase();
            img.src = imgSrc;
            modal.style.display = 'flex';

            if (cropper) cropper.destroy();

            cropper = new Cropper(img, {
                aspectRatio: NaN,
                viewMode: 1,
                autoCropArea: 1,
                responsive: true,
                movable: true,
                zoomable: true,
                rotatable: false,
                scalable: false,
                ready: function () {
                    cropper.setCropBoxData(cropper.getCanvasData());
                }
            });
        });
    }

    function closeCropperModal() {
        const modal = document.getElementById('cropper-modal');
        if (modal) modal.style.display = 'none';
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
    }

    function setupImageField(fieldName) {
        const input = document.querySelector('input[type="file"][name="' + fieldName + '"]');
        if (!input || input.dataset.cropperAttached) return;

        input.dataset.cropperAttached = 'true';

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'unfold-crop-trigger-btn';
        btn.title = 'Ajustar / Recortar ' + fieldName;
        btn.setAttribute('aria-label', 'Ajustar / Recortar ' + fieldName);
        btn.innerHTML = '<span class="material-symbols-outlined" style="font-size:18px; line-height:1;">crop</span>';

        input._cropBtn = btn;

        const target = input.closest('.fieldBox, .field, .form-row, div') || input.parentElement;
        if (target && target.parentElement) {
            const actionWrap = document.createElement('div');
            actionWrap.className = 'unfold-crop-trigger-wrap';
            actionWrap.appendChild(btn);
            target.parentElement.insertBefore(actionWrap, target.nextElementSibling);
        }

        const existingLink = (input.closest('.fieldBox, .field, .form-row') || input.parentElement || document.body).querySelector('a[href*="http"], a[href*="media"], a[href*="cloudinary"], a[href*="image"]');
        if (existingLink && existingLink.href) {
            btn.dataset.imgSrc = existingLink.href;
            btn.dataset.fileName = fieldName + '.jpg';
            btn.style.display = 'inline-flex';
        }

        input.addEventListener('change', function (e) {
            const files = e.target.files;
            if (files && files.length > 0) {
                if (files[0].isCropped) return;

                const file = files[0];
                const reader = new FileReader();
                reader.onload = function (evt) {
                    btn.dataset.imgSrc = evt.target.result;
                    btn.dataset.fileName = file.name;
                    btn.style.display = 'inline-flex';
                };
                reader.readAsDataURL(file);
            }
        });

        btn.addEventListener('click', function (e) {
            e.preventDefault();
            if (btn.dataset.imgSrc) {
                openCropperModal(fieldName, btn.dataset.imgSrc, btn.dataset.fileName, input);
            }
        });
    }

    function initAllCroppers() {
        setupImageField('portada');
        setupImageField('contraportada');
    }

    document.addEventListener('DOMContentLoaded', initAllCroppers);
    const observer = new MutationObserver(initAllCroppers);
    observer.observe(document.documentElement, { childList: true, subtree: true });
    setTimeout(initAllCroppers, 500);
})();