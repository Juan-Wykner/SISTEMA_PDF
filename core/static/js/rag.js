// Funções para melhorar a interação
document.addEventListener('DOMContentLoaded', function() {
    const questionInput = document.getElementById('pergunta');
    const hintItems = document.querySelectorAll('.hint-item');
    
    // Adicionar evento de clique nos itens de dica
    hintItems.forEach(item => {
        item.addEventListener('click', function() {
            questionInput.value = this.textContent;
            questionInput.focus();
        });
    });
    
    // Auto-resize do textarea
    questionInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
});