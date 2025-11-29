# Documentação do Sistema PDF

## Visão Geral
Sistema de processamento e análise de documentos PDF com funcionalidades de extração de dados e RAG (Retrieval-Augmented Generation).

## Funcionalidades
- Upload e processamento de arquivos PDF
- Extração de dados através de IA
- Sistema de perguntas e respostas via RAG
- Interface web intuitiva

## Estrutura do Projeto
```
SISTEMA_PDF/
├── config/                 # Configurações Django (renomeado de sistema_pdf)
├── core/                   # App principal
│   ├── agents/            # Agentes de IA
│   ├── infrastructure/    # Infraestrutura
│   └── templates/         # Templates HTML
├── docs/                  # Documentação
├── logs/                  # Arquivos de log
├── media/                 # Arquivos enviados
├── static/                # Arquivos estáticos
├── tests/                 # Testes
└── venv/                  # Ambiente virtual
```

## Instalação
1. Configure o ambiente virtual
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure as variáveis de ambiente no `.env`
4. Execute as migrações: `python manage.py migrate`
5. Inicie o servidor: `python manage.py runserver`

## Uso
- Acesse a página inicial para escolher entre upload de PDF ou consulta RAG
- Faça upload de documentos PDF para processamento
- Utilize o sistema RAG para fazer perguntas sobre os documentos processados