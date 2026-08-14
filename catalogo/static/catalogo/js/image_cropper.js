/* static/catalogo/js/image_cropper.js */

document.addEventListener('DOMContentLoaded', function () {
    const inputPortada = document.querySelector('input[type="file"][name="portada"]');
    if (!inputPortada) return;

    const cropButton = document.createElement('button');
    cropButton.type = 'button';
    cropButton.textContent = '✂️ Recortar imagen';
    cropButton.id = 'crop-image-button';
    cropButton.style.cssText = 'margin-top: 8px; display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 12px; border: 1px solid #cbd5e1; background: #f8fafc; color: #0f172a; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 14px;';
    inputPortada.insertAdjacentElement('afterend', cropButton);

    function getCurrentImageSource() {
        const fieldWrapper = inputPortada.closest('.field-portada, .form-row, .fieldBox, .field-box');
        if (fieldWrapper) {
            const img = fieldWrapper.querySelector('img');
            if (img && img.src) return img.src;

            const mediaLink = fieldWrapper.querySelector('a[href*="/media/"]');
            if (mediaLink && mediaLink.href) return mediaLink.href;
        }
        return null;
    }

    function updateCropButtonVisibility() {
        const hasSelectedFile = !!(inputPortada.files && inputPortada.files.length > 0);
        const shouldShow = hasSelectedFile || !!getCurrentImageSource();
        cropButton.hidden = !shouldShow;
        cropButton.style.display = shouldShow ? 'inline-flex' : 'none';
    }

    function openCropperWithFile(file) {
        const reader = new FileReader();
        reader.onload = function (evt) {
            imageElement.src = evt.target.result;
            modal.style.display = 'flex';

            if (cropper) {
                cropper.destroy();
            }

            cropper = new Cropper(imageElement, {
                aspectRatio: NaN,
                autoCrop: false,
                autoCropArea: 0,
                viewMode: 2,
                responsive: true,
                movable: true,
                zoomable: true,
                rotatable: false,
                scalable: false,
                dragMode: 'move',
                cropBoxMovable: true,
                cropBoxResizable: true,
                guides: false,
                center: false,
                highlight: false,
                background: false,
                checkCrossOrigin: false
            });

            cropper.clear();
        };
        reader.readAsDataURL(file);
    }

    const modalHTML = `
    <div id="cropper-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.75); z-index:99999; align-items:center; justify-content:center; padding:1rem;">
        <div style="background:#fff; border-radius:8px; max-width:650px; width:100%; overflow:hidden; display:flex; flex-direction:column; max-height:90vh; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.3);">
            <div style="padding:12px 16px; border-bottom:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center;">
                <h6 style="margin:0; font-weight:600; color:#1e293b;">Encuadre y Recorte de Portada</h6>
                <span id="close-cropper-x" style="cursor:pointer; font-size:20px; color:#64748b;">&times;</span>
            </div>
            <div style="padding:16px; background:#0f172a; flex:1; max-height:60vh; display:flex; justify-content:center; align-items:center; overflow:hidden;">
                <img id="image-to-crop" style="max-width:100%; max-height:100%; display:block;" />
            </div>
            <div style="padding:12px 16px; background:#f8fafc; border-top:1px solid #e2e8f0; display:flex; flex-wrap:wrap; gap:8px; justify-content:space-between; align-items:center;">
                <div style="display:flex; gap:6px;">
                    <button type="button" class="btn-ratio" data-ratio="0.666" style="padding:4px 8px; font-size:12px; border:1px solid #cbd5e1; border-radius:4px; background:#fff; cursor:pointer;">Libro (2:3)</button>
                    <button type="button" class="btn-ratio" data-ratio="0.75" style="padding:4px 8px; font-size:12px; border:1px solid #cbd5e1; border-radius:4px; background:#fff; cursor:pointer;">Estándar (3:4)</button>
                    <button type="button" class="btn-ratio" data-ratio="NaN" style="padding:4px 8px; font-size:12px; border:1px solid #cbd5e1; border-radius:4px; background:#fff; cursor:pointer;">Libre</button>
                </div>
                <div style="display:flex; gap:8px;">
                    <button type="button" id="cancel-crop" style="padding:6px 12px; border:1px solid #cbd5e1; background:#fff; border-radius:6px; cursor:pointer; font-size:13px;">Cancelar</button>
                    <button type="button" id="apply-crop" style="padding:6px 14px; border:none; background:#10b981; color:#fff; font-weight:600; border-radius:6px; cursor:pointer; font-size:13px;">Guardar Encuadre</button>
                </div>
            </div>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    const modal = document.getElementById('cropper-modal');
    const imageElement = document.getElementById('image-to-crop');
    const applyBtn = document.getElementById('apply-crop');
    const cancelBtn = document.getElementById('cancel-crop');
    const closeX = document.getElementById('close-cropper-x');
    const ratioBtns = document.querySelectorAll('.btn-ratio');

    let cropper = null;
    let originalFile = null;

    inputPortada.addEventListener('change', function () {
        const files = inputPortada.files;
        if (files && files.length > 0) {
            originalFile = files[0];
            if (originalFile.isCropped) return;
        }
        updateCropButtonVisibility();
    });

    cropButton.addEventListener('click', function () {
        if (inputPortada.files && inputPortada.files.length > 0) {
            originalFile = inputPortada.files[0];
            openCropperWithFile(originalFile);
            return;
        }

        const currentSource = getCurrentImageSource();
        if (!currentSource) {
            alert('Primero selecciona una imagen para recortarla.');
            return;
        }

        imageElement.src = currentSource;
        modal.style.display = 'flex';

        if (cropper) {
            cropper.destroy();
        }

        cropper = new Cropper(imageElement, {
            aspectRatio: NaN,
            autoCrop: false,
            autoCropArea: 0,
            viewMode: 2,
            responsive: true,
            movable: true,
            zoomable: true,
            rotatable: false,
            scalable: false,
            dragMode: 'move',
            cropBoxMovable: true,
            cropBoxResizable: true,
            guides: false,
            center: false,
            highlight: false,
            background: false,
            checkCrossOrigin: false
        });

        cropper.clear();
    });

    ratioBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const ratio = parseFloat(this.dataset.ratio);
            if (cropper) {
                cropper.setAspectRatio(isNaN(ratio) ? NaN : ratio);
            }
        });
    });

    applyBtn.addEventListener('click', function () {
        if (!cropper) return;

        const canvas = cropper.getCroppedCanvas({
            imageSmoothingEnabled: true,
            imageSmoothingQuality: 'high',
        });

        canvas.toBlob(function (blob) {
            if (!blob) return;

            const name = (originalFile && originalFile.name) ? originalFile.name : 'portada.jpg';
            const croppedFile = new File([blob], name, {
                type: 'image/jpeg',
                lastModified: Date.now()
            });
            croppedFile.isCropped = true;

            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(croppedFile);
            inputPortada.files = dataTransfer.files;

            closeModal();
        }, 'image/jpeg', 0.90);
    });

    function closeModal() {
        modal.style.display = 'none';
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
    }

    cancelBtn.addEventListener('click', closeModal);
    closeX.addEventListener('click', closeModal);
    updateCropButtonVisibility();
});
