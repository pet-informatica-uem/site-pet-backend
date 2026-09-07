FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/opt/poetry/bin:$PATH"

# locale pt_BR.UTF-8 (main.py) + poppler (pdf2image) + libs de imagem (Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
        locales poppler-utils libjpeg62-turbo zlib1g libfreetype6 \
    && sed -i 's/^# *pt_BR.UTF-8/pt_BR.UTF-8/' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-interaction --no-ansi

COPY . .
RUN poetry install --only main --no-interaction --no-ansi

EXPOSE 8000
CMD ["uvicorn", "main:petBack", "--host", "0.0.0.0", "--port", "8000"]
