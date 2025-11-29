// Funções melhoradas para upload
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('pdf-input');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const btnExtract = document.getElementById('btn-extract');

// Drag & Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'application/pdf') {
        handleFile(files[0]);
    } else {
        alert('Por favor, envie apenas arquivos PDF.');
    }
});

// Clique na área
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Mudança do input
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Função para lidar com o arquivo
function handleFile(file) {
    if (file.type !== 'application/pdf') {
        alert('Por favor, envie apenas arquivos PDF.');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB
        alert('O arquivo deve ter no máximo 10MB.');
        return;
    }
    
    fileName.textContent = file.name;
    const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
    fileSize.textContent = `${sizeInMB} MB`;
    
    fileInfo.style.display = 'block';
    btnExtract.style.display = 'flex';
    uploadArea.style.display = 'none';
}

// Remover arquivo
function removeFile() {
    fileInput.value = '';
    fileInfo.style.display = 'none';
    btnExtract.style.display = 'none';
    uploadArea.style.display = 'block';
}

// Loading ao enviar
const uploadForm = document.getElementById('upload-form');
uploadForm.addEventListener('submit', (e) => {
    if (!fileInput.files.length) {
        e.preventDefault();
        alert('Por favor, selecione um arquivo PDF.');
        return;
    }
    
    document.getElementById('loading').style.display = 'flex';
});