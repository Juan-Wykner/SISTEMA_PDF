// Função para inicializar a página de resultado de extração
(function () {
    try {
        var data = JSON.parse(document.getElementById('dados-json').textContent);
        document.getElementById('json-content').textContent = JSON.stringify(data, null, 2);
    } catch(e) {
        document.getElementById('json-content').textContent = 'Erro ao renderizar JSON.';
    }
})();

// Função para alternar entre abas
function openTab(ev, tabName) {
    var tabs = document.getElementsByClassName('tab-content');
    var buttons = document.getElementsByClassName('tab-button');
    
    // Esconder todas as abas
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
    }
    
    // Remover classe active de todos os botões
    for (var j = 0; j < buttons.length; j++) {
        buttons[j].classList.remove('active');
    }
    
    // Mostrar aba selecionada e marcar botão como ativo
    document.getElementById(tabName).classList.add('active');
    ev.currentTarget.classList.add('active');
}

// Função para copiar JSON para a área de transferência
function copyToClipboard() {
    var text = document.getElementById('json-content').textContent;
    
    // Usar a API moderna do clipboard se disponível
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function() {
            // Mostrar feedback visual
            var btn = document.querySelector('.btn-copy');
            var originalText = btn.textContent;
            btn.textContent = 'Copiado!';
            btn.style.background = '#28a745';
            
            setTimeout(function() {
                btn.textContent = originalText;
                btn.style.background = '#2563eb';
            }, 2000);
        }).catch(function(err) {
            // Fallback para método antigo se a API moderna falhar
            fallbackCopyToClipboard(text);
        });
    } else {
        // Fallback para navegadores mais antigos
        fallbackCopyToClipboard(text);
    }
}

// Função de fallback para copiar texto
function fallbackCopyToClipboard(text) {
    var textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        var btn = document.querySelector('.btn-copy');
        var originalText = btn.textContent;
        btn.textContent = 'Copiado!';
        btn.style.background = '#28a745';
        
        setTimeout(function() {
            btn.textContent = originalText;
            btn.style.background = '#2563eb';
        }, 2000);
    } catch (err) {
        alert('Erro ao copiar texto. Por favor, copie manualmente.');
    }
    
    document.body.removeChild(textArea);
}