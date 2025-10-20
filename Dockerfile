FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (minimal for sqlite and Pillow if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Django collectstatic (no input) - safe if WhiteNoise configured
ENV DJANGO_SETTINGS_MODULE=sistema_pdf.settings
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "sistema_pdf.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]


