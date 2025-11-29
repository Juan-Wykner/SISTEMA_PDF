// JavaScript para o Extrator de NF - Versão simplificada

document.addEventListener('DOMContentLoaded', function() {
    console.log('Script carregado com sucesso!');
    
    // File upload handling (apenas se elementos existirem)
    const fileInput = document.getElementById('id_pdf_file');
    const fileLabel = document.querySelector('.file-label');
    const fileName = document.querySelector('.file-name');
    
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (fileName) {
                    fileName.textContent = file.name;
                }
                fileLabel.classList.add('has-file');
            } else {
                if (fileName) {
                    fileName.textContent = 'Nenhum arquivo selecionado';
                }
                fileLabel.classList.remove('has-file');
            }
        });
    }
    
    // Loading states for forms (apenas se formulários existirem)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loading"></span> Processando...';
            }
        });
    });
    
    // Copy JSON functionality (apenas se botões existirem)
    const copyButtons = document.querySelectorAll('.copy-json-btn');
    copyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const text = targetElement.textContent;
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(text).then(() => {
                        const originalText = this.textContent;
                        this.textContent = 'Copiado!';
                        this.classList.add('copied');
                        
                        setTimeout(() => {
                            this.textContent = originalText;
                            this.classList.remove('copied');
                        }, 2000);
                    }).catch(err => {
                        console.log('Erro ao copiar:', err);
                    });
                }
            }
        });
    });
    
    // Auto-resize textareas (apenas se textareas existirem)
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});

// Utility functions
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    document.body.insertBefore(alertDiv, document.body.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}