# SISTEMA_PDF

Aplicação Django para processamento e validação de PDFs com foco em clareza, simplicidade e consistência.

## Visão Geral
- Interface para upload de PDF e extração dos dados (`core.views`).
- Validação interativa e criação de cadastros relacionados (`core.views_validacao`).
- Extração de texto do PDF e análise via agente LLM (`core.services` e `core.agents`).

## Arquitetura (Camadas)
- Domínio/Negócio: `core.models` (Pessoas, Classificação, Movimento/Parcela, MovimentoClassificação).
- Infraestrutura: `core/infrastructure/file_storage.py` (gravação/remoção de arquivos temporários).
- Interface/UI: `core/views.py`, `core/views_validacao.py` e templates em `core/templates/core/`.

Princípios adotados:
- Clareza acima de tudo: nomes significativos e responsabilidades explícitas.
- Simplicidade antes de complexidade: evitar abstrações desnecessárias.
- Consistência: mesmo estilo e convenções em todo o projeto.
- SRP: funções/módulos com uma responsabilidade clara.
- DRY: lógica comum centralizada.

## Qualidade de Código
- Formatador: Black (`pyproject.toml`).
- Ordenação de imports: isort (perfil Black).
- Linter: Pylint (configuração em `.pylintrc`).

Comandos úteis (ambiente local):
```bash
# Formatador e imports
black .
isort .

# Linter
pylint core sistema_pdf

# Testes
python manage.py test
```

## Fluxo de Uso
1. Acesse a página inicial e envie um PDF.
2. O sistema extrai o texto do PDF e envia ao agente para análise.
3. Você pode validar/ajustar cadastros pela interface interativa em `/validacao/`.
4. Após validar, é possível criar o lançamento financeiro correlato.

## Execução com Docker

1. Build da imagem:
```bash
docker compose build
```

2. Migrações e subir app:
```bash
docker compose run --rm web python manage.py migrate
docker compose up -d
```

3. Coletar estáticos (se necessário):
```bash
docker compose run --rm web python manage.py collectstatic --noinput
```

4. Acessar:
- `http://localhost:8000`

## Variáveis de Ambiente
- `DEBUG`
- `ALLOWED_HOSTS`
- `GEMINI_API_KEY`

## Desenvolvimento Local (sem Docker)
1. Crie um virtualenv.
2. Instale dependências: `pip install -r requirements.txt`.
3. Rode: `python manage.py runserver`.

## Convenções de Commits e Branches
- Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
- Branches: `feat/<resumo>`, `fix/<resumo>`, `refactor/<resumo>`.

## Dependências
- Evite adicionar libs desnecessárias; prefira composição a herança.
- Documente decisões e mantenha o projeto simples e transparente.
