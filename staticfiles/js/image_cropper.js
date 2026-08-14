/* static/js/image_cropper.js */

(function () {
    let cropper = null;
    let activeInput = null;
    let activeImageSrc = null;
    let activeFileName = 'imagen_recortada.jpg';

    // 1. Inyectar estilos CSS dedicados para Modo Claro y Modo Oscuro
    function injectThemeStyles() {
        if (document.getElementById('cropper-custom-styles')) return;

        const styleEl = document.createElement('style');
        styleEl.id = 'cropper-custom-styles';
        styleEl.innerHTML = `
            /* Variables de tema base (Modo Claro) */
            :root {
                --crop-bg-modal: #ffffff;
                --crop-bg-header: #f8fafc;
                --crop-bg-footer: #f8fafc;
                --crop-border: #e2e8f0;
                --crop-text-main: #341e3b;
                --crop-text-muted: #78648b;
                --crop-btn-bg: #ffffff;
                --crop-btn-hover: #f1f5f9;
                --crop-accent: #9c25eb;
                --crop-accent-bg: #eff6ff;
            }

            /* Detección de Modo Oscuro de Unfold / Sistema */
            html.dark, body.dark, [data-theme="dark"] {
                --crop-bg-modal: #1e293b !important;
                --crop-bg-header: #0f172a !important;
                --crop-bg-footer: #0f172a !important;
                --crop-border: #433355 !important;
                --crop-text-main: #f8fafc !important;
                --crop-text-muted: #a594b8 !important;
                --crop-btn-bg: #4e3355 !important;
                --crop-btn-hover: #5b4769 !important;
                --crop-accent: #c960fa !important;
                --crop-accent-bg: #591e8a !important;
            }

            /* Contenedor exterior para mantener barra y botón juntos por fuera */
            .unfold-crop-outer-wrap {
                display: inline-flex !important;
                align-items: center !important;
                gap: 8px !important;
                width: auto !important;
                max-width: 100% !important;
                vertical-align: middle !important;
            }

            /* Botón disparador exterior */
            .unfold-crop-trigger-btn {
                display: none;
                height: 38px;
                min-width: 38px;
                width: 38px;
                padding: 0;
                border-radius: 6px;
                cursor: pointer;
                align-items: center;
                justify-content: center;
                background-color: var(--crop-btn-bg);
                color: var(--crop-accent);
                border: 1px solid var(--crop-border);
                transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
                white-space: nowrap;
                flex-shrink: 0;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            }
            .unfold-crop-trigger-btn:hover {
                background-color: var(--crop-btn-hover);
                border-color: var(--crop-accent);
            }

            /* Modal y contenedores */
            .unfold-crop-modal-card {
                background-color: var(--crop-bg-modal);
                border: 1px solid var(--crop-border);
                color: var(--crop-text-main);
            }
            .unfold-crop-header {
                background-color: var(--crop-bg-header);
                border-bottom: 1px solid var(--crop-border);
            }
            .unfold-crop-footer {
                background-color: var(--crop-bg-footer);
                border-top: 1px solid var(--crop-border);
            }
            .unfold-crop-ratio-btn {
                padding: 5px 12px;
                font-size: 12px;
                font-weight: 500;
                border-radius: 6px;
                cursor: pointer;
                background-color: var(--crop-btn-bg);
                color: var(--crop-text-main);
                border: 1px solid var(--crop-border);
            }
            .unfold-crop-ratio-btn.active {
                background-color: var(--crop-accent-bg) !important;
                color: var(--crop-accent) !important;
                border-color: var(--crop-accent) !important;
                font-weight: 600;
            }
            .unfold-crop-cancel-btn {
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 500;
                border-radius: 6px;
                cursor: pointer;
                background-color: var(--crop-btn-bg);
                color: var(--crop-text-main);
                border: 1px solid var(--crop-border);
            }
            .unfold-crop-cancel-btn:hover {
                background-color: var(--crop-btn-hover);
            }
        `;
        document.head.appendChild(styleEl);
    }

    // 2. Inyectar Modal en el DOM
    function ensureModalExists() {
        injectThemeStyles();
        if (document.getElementById('cropper-modal')) return;

        const modalHTML = `
        <div id="cropper-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.85); backdrop-filter:blur(4px); z-index:999999; align-items:center; justify-content:center; padding:1rem;">
            <div class="unfold-crop-modal-card" style="border-radius:10px; max-width:720px; width:100%; overflow:hidden; display:flex; flex-direction:column; max-height:90vh; box-shadow:0 25px 50px -12px rgba(0,0,0,0.6);">
                
                <!-- Modal Header -->
                <div class="unfold-crop-header" style="padding:12px 18px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="material-symbols-outlined" style="font-size:18px; color:var(--crop-accent);">crop</span>
                        <h6 id="cropper-modal-title" style="margin:0; font-weight:600; font-size:14px; color:var(--crop-text-main);">Encuadre y Recorte</h6>
                    </div>
                    <button type="button" id="close-cropper-x" style="background:none; border:none; font-size:22px; color:var(--crop-text-muted); cursor:pointer; line-height:1;">&times;</button>
                </div>
                
                <!-- Image Box -->
                <div style="padding:12px; background:#0b0f19; flex:1; max-height:58vh; display:flex; justify-content:center; align-items:center; overflow:hidden;">
                    <img id="image-to-crop" style="max-width:100%; max-height:100%; display:block;" />
                </div>

                <!-- Footer / Controls -->
                <div class="unfold-crop-footer" style="padding:12px 18px; display:flex; flex-wrap:wrap; gap:10px; justify-content:space-between; align-items:center;">
                    <div style="display:flex; gap:6px;">
                        <button type="button" class="unfold-crop-ratio-btn active" data-ratio="NaN">Libre</button>
                        <button type="button" class="unfold-crop-ratio-btn" data-ratio="0.666">Libro (2:3)</button>
                        <button type="button" class="unfold-crop-ratio-btn" data-ratio="0.75">Estándar (3:4)</button>
                    </div>
                    
                    <div style="display:flex; gap:8px;">
                        <button type="button" id="cancel-crop-btn" class="unfold-crop-cancel-btn">Cancelar</button>
                        <button type="button" id="apply-crop-btn" style="padding:6px 16px; border:none; background:#10b981; color:#ffffff; font-weight:600; font-size:12px; border-radius:6px; cursor:pointer;">Guardar Recorte</button>
                    </div>
                </div>

            </div>
        </div>`;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        const modal = document.getElementById('cropper-modal');
        document.getElementById('cancel-crop-btn').onclick = closeCropperModal;
        document.getElementById('close-cropper-x').onclick = closeCropperModal;

        const ratioBtns = modal.querySelectorAll('.unfold-crop-ratio-btn');
        ratioBtns.forEach(btn => {
            btn.onclick = function () {
                ratioBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                const ratio = parseFloat(this.dataset.ratio);
                if (cropper) {
                    cropper.setAspectRatio(isNaN(ratio) ? NaN : ratio);
                }
            };
        });

        document.getElementById('apply-crop-btn').onclick = function () {
            if (!cropper || !activeInput) return;

            const canvas = cropper.getCroppedCanvas({
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high'
            });

            canvas.toBlob(function (blob) {
                const cleanName = (activeFileName || 'imagen.jpg').replace(/\.[^/.]+$/, "") + ".jpg";
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

    function openCropperModal(fieldName, imgSrc, fileName, inputElem) {
        ensureModalExists();
        const modal = document.getElementById('cropper-modal');
        const img = document.getElementById('image-to-crop');
        const title = document.getElementById('cropper-modal-title');

        activeInput = inputElem;
        activeImageSrc = imgSrc;
        activeFileName = fileName || 'portada.jpg';

        title.textContent = `Ajustar / Recortar ${fieldName.toUpperCase()}`;
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
                this.cropper.setCropBoxData(this.cropper.getCanvasData());
            }
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

    // 3. Configurar campos de formulario insertando el botón FUERA de la barra pero a su lado
    function setupImageField(fieldName) {
        injectThemeStyles();
        const input = document.querySelector(`input[type="file"][name="${fieldName}"]`);
        if (!input || input.dataset.cropperAttached) return;

        input.dataset.cropperAttached = "true";

        const container = input.closest('.form-row') || input.closest('div') || input.parentElement;

        // Crear el botón
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'unfold-crop-trigger-btn';
        btn.title = `Ajustar / Recortar ${fieldName}`;
        btn.setAttribute('aria-label', `Ajustar / Recortar ${fieldName}`);
        btn.innerHTML = `<span class="material-symbols-outlined" style="font-size:18px; line-height:1;">crop</span>`;
        input._cropBtn = btn;

        // Identificar el bloque exterior completo que forma la "barra" del archivo
        const existingLink = container.querySelector('a[href*="http"], a[href*="media"], a[href*="cloudinary"], a[href*="image"]');
        
        // Obtenemos el bloque de la barra visible completa
        const fileBarBlock = existingLink
            ? (existingLink.closest('.flex, .border, p, div') || existingLink.parentElement)
            : (input.closest('.flex, .relative, div') || input);

        // Envolver la barra completa y el botón en un contenedor inline conjunto
        if (fileBarBlock && fileBarBlock.parentElement) {
            let outerWrap = fileBarBlock.parentElement.classList.contains('unfold-crop-outer-wrap')
                ? fileBarBlock.parentElement
                : null;

            if (!outerWrap) {
                outerWrap = document.createElement('div');
                outerWrap.className = 'unfold-crop-outer-wrap';
                fileBarBlock.parentNode.insertBefore(outerWrap, fileBarBlock);
                outerWrap.appendChild(fileBarBlock);
            }
            
            // Insertar el botón a la derecha por fuera de la barra
            outerWrap.appendChild(btn);
        } else {
            input.insertAdjacentElement('afterend', btn);
        }

        if (existingLink && existingLink.href) {
            btn.dataset.imgSrc = existingLink.href;
            btn.dataset.fileName = `${fieldName}.jpg`;
            btn.style.display = 'inline-flex';
        }

        // Detectar si se sube una nueva imagen desde el explorador
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