# SISTEMA_PDF

Aplicação Django para processamento e validação de PDFs.

## Requisitos
- Docker e Docker Compose

## Como executar com Docker

1. Build da imagem:
```bash
docker compose build
```

2. Rodar migrações e subir app:
```bash
docker compose run --rm web python manage.py migrate
docker compose up -d
```

3. Coletar estáticos (se necessário):
```bash
docker compose run --rm web python manage.py collectstatic --noinput
```

4. Acessar:
- http://localhost:8000

## Variáveis de ambiente
- `DEBUG` (default False no compose)
- `ALLOWED_HOSTS` (default `*` no compose)
- `GEMINI_API_KEY` (opcional)

## Desenvolvimento local sem Docker
Crie um virtualenv, instale `requirements.txt` e rode `python manage.py runserver`.
