// Variáveis globais
let dadosValidacao = null;
let cadastrosPendentes = {
    fornecedor: false,
    faturado: false,
    classificacoes: []
};

// Inicialização ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    // Obter dados do script JSON
    const dadosJsonElement = document.getElementById('dados-json');
    if (dadosJsonElement) {
        dadosValidacao = JSON.parse(dadosJsonElement.textContent);
        console.log('Dados carregados:', dadosValidacao);
        
        // Adaptar estrutura para o formato esperado
        if (dadosValidacao.fornecedor && !dadosValidacao.fornecedor.razao_social) {
            dadosValidacao.fornecedor.razao_social = dadosValidacao.fornecedor.razao_social || '';
        }
        if (dadosValidacao.faturado && !dadosValidacao.faturado.nome_completo) {
            dadosValidacao.faturado.nome_completo = dadosValidacao.faturado.nome || '';
        }
        if (dadosValidacao.classificacoes && !dadosValidacao.classificacao_despesa) {
            dadosValidacao.classificacao_despesa = dadosValidacao.classificacoes;
        }
        
        adicionarLog('Interface de validação carregada com dados do PDF', 'info');
    }
});

// Função para iniciar validação
function iniciarValidacao() {
    if (!dadosValidacao) {
        alert('Erro: Dados não carregados corretamente');
        return;
    }
    
    // Resetar cadastros pendentes
    cadastrosPendentes = {
        fornecedor: false,
        faturado: false,
        classificacoes: []
    };
    
    // Limpar botões anteriores
    document.getElementById('lista-botoes-criacao').innerHTML = '';
    document.getElementById('botoes-criacao').style.display = 'none';
    document.getElementById('finalizar-section').style.display = 'none';
    
    // Atualizar progresso
    atualizarProgresso(0, 'Iniciando validação dos cadastros...');
    adicionarLog('Iniciando validação dos cadastros...', 'info');
    
    // Desabilitar botão de iniciar
    document.getElementById('btn-iniciar-validacao').disabled = true;
    
    // Iniciar validações sequenciais
    setTimeout(() => validarFornecedor(), 500);
}

async function validarFornecedor() {
    atualizarProgresso(25, 'Validando fornecedor...');
    adicionarLog('Validando fornecedor...', 'info');
    
    try {
        const cnpj = dadosValidacao.fornecedor.cnpj.replace(/[^\d]/g, '');
        const response = await fetch('/api/validar-fornecedor/?cnpj=' + encodeURIComponent(cnpj), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        const resultado = await response.json();
        
        atualizarStatusFornecedor(resultado);
        
        // Continuar para próxima validação
        setTimeout(() => validarFaturado(), 1000);
        
    } catch (error) {
        adicionarLog(`Erro ao validar fornecedor: ${error.message}`, 'error');
        atualizarProgresso(25, 'Erro na validação do fornecedor');
    }
}

async function validarFaturado() {
    atualizarProgresso(50, 'Validando faturado...');
    adicionarLog('Validando faturado...', 'info');
    
    try {
        const cpf = dadosValidacao.faturado.cpf.replace(/[^\d]/g, '');
        const response = await fetch('/api/validar-faturado/?cpf=' + encodeURIComponent(cpf), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        const resultado = await response.json();
        
        atualizarStatusFaturado(resultado);
        
        // Continuar para próxima validação
        setTimeout(() => validarClassificacoes(), 1000);
        
    } catch (error) {
        adicionarLog(`Erro ao validar faturado: ${error.message}`, 'error');
        atualizarProgresso(50, 'Erro na validação do faturado');
    }
}

async function validarClassificacoes() {
    atualizarProgresso(75, 'Validando classificações...');
    adicionarLog('Validando classificações...', 'info');
    
    if (!dadosValidacao.classificacao_despesa || dadosValidacao.classificacao_despesa.length === 0) {
        adicionarLog('Nenhuma classificação para validar', 'info');
        concluirValidacao();
        return;
    }
    
    try {
        for (let i = 0; i < dadosValidacao.classificacao_despesa.length; i++) {
            const descricao = dadosValidacao.classificacao_despesa[i];
            const response = await fetch('/api/validar-classificacao/?descricao=' + encodeURIComponent(descricao));
            const resultado = await response.json();
            
            atualizarStatusClassificacao(i, descricao, resultado);
            
            // Pequena pausa entre validações
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        concluirValidacao();
        
    } catch (error) {
        adicionarLog(`Erro ao validar classificações: ${error.message}`, 'error');
        atualizarProgresso(75, 'Erro na validação das classificações');
    }
}

function concluirValidacao() {
    // Decide UI após validar classificações
    const temPendentes = cadastrosPendentes.fornecedor ||
                         cadastrosPendentes.faturado ||
                         cadastrosPendentes.classificacoes.length > 0;

    if (temPendentes) {
        document.getElementById('botoes-criacao').style.display = 'block';
        atualizarProgresso(90, 'Há cadastros pendentes para criação.');
        adicionarLog('Validação concluída. Crie os cadastros pendentes.', 'warning');
    } else {
        document.getElementById('finalizar-section').style.display = 'block';
        atualizarProgresso(100, 'Validação concluída. Pronto para criar lançamento.');
        adicionarLog('Todos os cadastros validados. Pronto para finalizar.', 'success');
    }
}

// Funções para atualizar status na interface
function atualizarStatusFornecedor(resultado) {
    const statusElement = document.getElementById('fornecedor-status');
    
    if (resultado.existe && resultado.ativo !== false) {
        statusElement.className = 'status success';
        statusElement.innerHTML = '<span class="status-icon">✓</span><span class="status-text">Cadastro existente</span>';
        adicionarLog(`Fornecedor encontrado: ${resultado.mensagem}`, 'success');
    } else if (resultado.existe && resultado.ativo === false) {
        statusElement.className = 'status warning';
        statusElement.innerHTML = '<span class="status-icon">!</span><span class="status-text">Cadastro inativo</span> <button id="btn-reativar-fornecedor" class="btn-create-item">Reativar</button>';
        document.getElementById('btn-reativar-fornecedor').onclick = async () => {
            adicionarLog('Reativando fornecedor...', 'info');
            const resp = await fetch('/api/reativar-fornecedor/', {method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken': getCookie('csrftoken')},body: JSON.stringify({cnpj: dadosValidacao.fornecedor.cnpj})});
            const rj = await resp.json();
            if (rj.sucesso){
                statusElement.className = 'status success';
                statusElement.innerHTML = '<span class="status-icon">✓</span><span class="status-text">Reativado</span>';
                adicionarLog('Fornecedor reativado com sucesso', 'success');
            } else {
                adicionarLog(`Falha ao reativar fornecedor: ${rj.erro}`, 'error');
            }
        };
    } else {
        statusElement.className = 'status error';
        statusElement.innerHTML = '<span class="status-icon">✗</span><span class="status-text">Cadastro não existe</span>';
        cadastrosPendentes.fornecedor = true;
        adicionarBotaoCriacao('fornecedor', 'Fornecedor', {
            cnpj: dadosValidacao.fornecedor.cnpj,
            razao_social: dadosValidacao.fornecedor.razao_social,
            nome_fantasia: dadosValidacao.fornecedor.nome_fantasia || ''
        });
        adicionarLog(`Fornecedor não encontrado: ${resultado.mensagem}`, 'warning');
    }
}

function atualizarStatusFaturado(resultado) {
    const statusElement = document.getElementById('faturado-status');
    
    if (resultado.existe && resultado.ativo !== false) {
        statusElement.className = 'status success';
        statusElement.innerHTML = '<span class="status-icon">✓</span><span class="status-text">Cadastro existente</span>';
        adicionarLog(`Faturado encontrado: ${resultado.mensagem}`, 'success');
    } else if (resultado.existe && resultado.ativo === false) {
        statusElement.className = 'status warning';
        statusElement.innerHTML = '<span class="status-icon">!</span><span class="status-text">Cadastro inativo</span> <button id="btn-reativar-faturado" class="btn-create-item">Reativar</button>';
        document.getElementById('btn-reativar-faturado').onclick = async () => {
            adicionarLog('Reativando faturado...', 'info');
            const resp = await fetch('/api/reativar-faturado/', {method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken': getCookie('csrftoken')},body: JSON.stringify({cpf: dadosValidacao.faturado.cpf})});
            const rj = await resp.json();
            if (rj.sucesso){
                statusElement.className = 'status success';
                statusElement.innerHTML = '<span class="status-icon">✓</span><span class="status-text">Reativado</span>';
                adicionarLog('Faturado reativado com sucesso', 'success');
            } else {
                adicionarLog(`Falha ao reativar faturado: ${rj.erro}`, 'error');
            }
        };
    } else {
        statusElement.className = 'status error';
        statusElement.innerHTML = '<span class="status-icon">✗</span><span class="status-text">Cadastro não existe</span>';
        cadastrosPendentes.faturado = true;
        adicionarBotaoCriacao('faturado', 'Faturado', {
            cpf: dadosValidacao.faturado.cpf,
            nome: dadosValidacao.faturado.nome_completo
        });
        adicionarLog(`Faturado não encontrado: ${resultado.mensagem}`, 'warning');
    }
}

function atualizarStatusClassificacao(index, descricao, resultado) {
    const classificacoes = document.querySelectorAll('.classificacao-item');
    const statusElement = classificacoes[index].querySelector('.status');
    
    if (resultado.existe && resultado.ativo !== false) {
        statusElement.className = 'status success';
        statusElement.innerHTML = '<span class="status-icon">✓</span><span class="status-text">Existe</span>';
        adicionarLog(`Classificação encontrada: ${resultado.mensagem}`, 'success');
    } else if (resultado.existe && resultado.ativo === false) {
        statusElement.className = 'status warning';
        const btnId = `btn-reativar-class-${index}`;
        statusElement.innerHTML = `<span class="status-icon">!</span><span class="status-text">Inativa</span> <button class="btn-create-item" id="${btnId}">Reativar</button>`;
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.onclick = async () => {
                adicionarLog(`Reativando classificação ${descricao}...`, 'info');
                const resp = await fetch('/api/reativar-classificacao/', {method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken': getCookie('csrftoken')},body: JSON.stringify({descricao, tipo:'DESPESA'})});
                const rj = await resp.json();
                if (rj.sucesso){
                    statusElement.className = 'status success';
                    statusElement.innerHTML = '<span class="status-icon">✓</span><span class="status-text">Reativada</span>';
                    adicionarLog('Classificação reativada com sucesso', 'success');
                } else {
                    adicionarLog(`Falha ao reativar classificação: ${rj.erro}`, 'error');
                }
            };
        } else {
            adicionarLog('Erro: botão de reativação não encontrado para classificação.', 'error');
        }
    } else {
        statusElement.className = 'status error';
        statusElement.innerHTML = '<span class="status-icon">✗</span><span class="status-text">Não existe</span>';
        cadastrosPendentes.classificacoes.push({
            index: index,
            descricao: descricao
        });
        adicionarBotaoCriacao('classificacao', `Classificação: ${descricao}`, {
            descricao: descricao,
            tipo: 'DESPESA'
        });
        adicionarLog(`Classificação não encontrada: ${resultado.mensagem}`, 'warning');
    }
}

// Função para adicionar botões de criação
function adicionarBotaoCriacao(tipo, titulo, dados) {
    const botoesCriacao = document.getElementById('botoes-criacao');
    const listaBotoes = document.getElementById('lista-botoes-criacao');
    
    botoesCriacao.style.display = 'block';
    
    const botao = document.createElement('button');
    botao.className = 'btn-create-item';
    botao.id = `btn-criar-${tipo}-${Date.now()}`;
    botao.innerHTML = `<span class="btn-icon">+</span> Criar ${titulo}`;
    botao.onclick = () => criarCadastro(tipo, titulo, dados, botao);
    
    listaBotoes.appendChild(botao);
}

// Função para criar cadastro no banco
async function criarCadastro(tipo, titulo, dados, botaoElemento) {
    botaoElemento.disabled = true;
    botaoElemento.innerHTML = '<span class="loading"></span> Criando...';
    
    adicionarLog(`Iniciando criação de ${titulo}...`, 'info');
    
    try {
        let endpoint;
        let dadosEnvio = { ...dados };
        
        // Preparar dados específicos para cada tipo
        if (tipo === 'fornecedor') {
            endpoint = '/api/criar-fornecedor/';
            dadosEnvio.tipo = 'FORNECEDOR';
        } else if (tipo === 'faturado') {
            endpoint = '/api/criar-faturado/';
            dadosEnvio.tipo = 'FATURADO';
            dadosEnvio.nome_completo = dados.nome;
        } else if (tipo === 'classificacao') {
            endpoint = '/api/criar-classificacao/';
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(dadosEnvio)
        });
        
        const resultado = await response.json();
        
        if (resultado.sucesso) {
            adicionarLog(`${titulo} criado com sucesso! ID: ${resultado.id}`, 'success');
            botaoElemento.innerHTML = '<span class="btn-icon">✓</span> Criado com sucesso';
            botaoElemento.style.background = '#28a745';
            botaoElemento.style.color = 'white';
            botaoElemento.style.borderColor = '#28a745';
            
            // Atualizar status pendente
            if (tipo === 'fornecedor') {
                cadastrosPendentes.fornecedor = false;
            } else if (tipo === 'faturado') {
                cadastrosPendentes.faturado = false;
            } else if (tipo === 'classificacao') {
                // Remover da lista de pendentes
                cadastrosPendentes.classificacoes = cadastrosPendentes.classificacoes.filter(
                    c => c.descricao !== dados.descricao
                );
            }
            
            verificarCadastrosPendentes();
        } else {
            adicionarLog(`Erro ao criar ${titulo}: ${resultado.erro}`, 'error');
            botaoElemento.disabled = false;
            botaoElemento.innerHTML = `<span class="btn-icon">+</span> Tentar novamente - ${titulo}`;
        }
        
    } catch (error) {
        adicionarLog(`Erro ao criar ${titulo}: ${error.message}`, 'error');
        botaoElemento.disabled = false;
        botaoElemento.innerHTML = `<span class="btn-icon">+</span> Tentar novamente - ${titulo}`;
    }
}

// Função para verificar se ainda há cadastros pendentes
function verificarCadastrosPendentes() {
    const temPendentes = cadastrosPendentes.fornecedor || 
                        cadastrosPendentes.faturado || 
                        cadastrosPendentes.classificacoes.length > 0;
    
    if (!temPendentes) {
        document.getElementById('finalizar-section').style.display = 'block';
        adicionarLog('Todos os cadastros foram validados/criados!', 'success');
    }
}

// Função para finalizar e criar lançamento
async function finalizarProcesso() {
    const btnFinalizar = document.getElementById('btn-finalizar');
    btnFinalizar.disabled = true;
    btnFinalizar.innerHTML = '<span class="loading"></span> Processando...';
    
    adicionarLog('Iniciando criação do lançamento...', 'info');
    
    try {
        const response = await fetch('/api/criar-lancamento/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(dadosValidacao)
        });
        
        const resultado = await response.json();
        
        if (resultado.sucesso) {
            adicionarLog(`Lançamento criado com sucesso! ID: ${resultado.id}`, 'success');
            alert(`Processo concluído com sucesso! Lançamento criado com ID: ${resultado.id}`);
            
            // Opcional: redirecionar ou limpar interface
            setTimeout(() => {
                window.location.href = '/';
            }, 3000);
        } else {
            adicionarLog(`Erro ao criar lançamento: ${resultado.erro}`, 'error');
            btnFinalizar.disabled = false;
            btnFinalizar.innerHTML = '<span class="btn-icon">✓</span> Todos os Cadastros Validados - Criar Lançamento';
        }
        
    } catch (error) {
        adicionarLog(`Erro ao criar lançamento: ${error.message}`, 'error');
        btnFinalizar.disabled = false;
        btnFinalizar.innerHTML = '<span class="btn-icon">✓</span> Todos os Cadastros Validados - Criar Lançamento';
    }
}

// Funções auxiliares
function atualizarProgresso(porcentagem, texto) {
    document.getElementById('progress-fill').style.width = porcentagem + '%';
    document.getElementById('progress-text').textContent = texto;
}

function adicionarLog(mensagem, tipo) {
    const logContent = document.getElementById('log-conteudo');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${tipo}`;
    
    const timestamp = new Date().toLocaleTimeString();
    logEntry.innerHTML = `<strong>[${timestamp}]</strong> ${mensagem}`;
    
    logContent.appendChild(logEntry);
    logContent.scrollTop = logContent.scrollHeight;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
